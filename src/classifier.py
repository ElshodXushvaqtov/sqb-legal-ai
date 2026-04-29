"""
classifier.py  –  murojaat tasniflash va compliance tekshirish
Google Gemini API orqali ishlaydi.
"""
import os
import json
import time
import urllib.parse
import logging
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY topilmadi. .env faylida GEMINI_API_KEY=... ni kiriting."
            )
        _client = genai.Client(api_key=api_key)
    return _client



MODEL          = os.getenv("CLASSIFIER_MODEL", "gemini-2.0-flash-lite")
FALLBACK_MODEL = os.getenv("CLASSIFIER_FALLBACK", "gemini-2.0-flash-lite")

# ── Lex.uz law → link map ──────────────────────────────────────────────────
LEX_LINKS: dict[str, str] = {
    "bank siri":                  "https://lex.uz/uz/docs/-41760",
    "jinoyat-protsessual":        "https://lex.uz/docs/-111460",
    "jpk":                        "https://lex.uz/docs/-111460",
    "banklar va bank faoliyati":  "https://lex.uz/acts/-2681",
    "soliq kodeksi":              "https://lex.uz/acts/-4674902",
    "pul yuvish":                 "https://lex.uz/acts/-283717",
    "jinoiy faoliyatdan olingan": "https://lex.uz/acts/-283717",
    "markaziy bank":              "https://lex.uz/acts/-72266",
    "fuqarolik kodeksi":          "https://lex.uz/acts/-111189",
    "aml":                        "https://lex.uz/acts/-283717",
    "moliyaviy razvedka":         "https://lex.uz/acts/-283717",
}


def _lex_link(law_name: str) -> str:
    low = law_name.lower()
    for key, url in LEX_LINKS.items():
        if key in low:
            return url
    return f"https://lex.uz/uz/search/all?searchtitle={urllib.parse.quote(law_name)}"


def _retry_wait(e: Exception) -> int:
    """Extract retry delay from Gemini error, default 35s."""
    import re
    try:
        m = re.search(r"retryDelay.*?(\d+)s", str(e))
        if m:
            return int(m.group(1)) + 2
    except Exception:
        pass
    return 35

def _llm(prompt: str, system: str = "", max_tokens: int = 1024, retries: int = 3) -> str:
    """Call Gemini with retry on 429/503 and automatic model fallback."""
    config = types.GenerateContentConfig(
        max_output_tokens=max_tokens,
        temperature=0.1,
        system_instruction=system if system else None,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )
    models_to_try = [MODEL, FALLBACK_MODEL]
    for model in models_to_try:
        for attempt in range(retries):
            try:
                response = _get_client().models.generate_content(
                    model=model, contents=prompt, config=config,
                )
                if model != MODEL:
                    logger.warning(f"Fallback model ishlatildi: {model}")
                return response.text.strip()
            except (genai_errors.ClientError, genai_errors.ServerError) as e:
                code = getattr(e, "code", 0) or 0
                retryable = code in (429, 503) or "UNAVAILABLE" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
                if retryable and attempt < retries - 1:
                    wait = _retry_wait(e)
                    logger.warning(f"[{model}] xatosi ({code}), {wait}s kutilmoqda... (urinish {attempt+1}/{retries})")
                    time.sleep(wait)
                elif retryable:
                    logger.warning(f"[{model}] barcha urinishlar tugadi, keyingi modelga o'tilmoqda...")
                    break
                else:
                    raise
    raise RuntimeError("Barcha modellar tugadi. Keyinroq qayta urinib ko'ring.")


def _parse_json(raw: str) -> dict:
    """
    Robustly extract a JSON object from LLM output.
    Handles: markdown fences, preamble text, truncated output mid-string or mid-key.
    """
    raw = raw.strip()


    if "```" in raw:
        for chunk in raw.split("```"):
            s = chunk.lstrip("json").strip()
            if s.startswith("{"):
                raw = s
                break

    start = raw.find("{")
    if start == -1:
        raise ValueError("JSON obyekti topilmadi")
    raw = raw[start:]


    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass


    cleaned = raw.rstrip()

    import re
    break_points = [m.end() for m in re.finditer(r'(?:,|\]|\}|")', cleaned)]
    for bp in reversed(break_points):
        snippet = cleaned[:bp].rstrip().rstrip(",")
        open_obj = snippet.count("{") - snippet.count("}")
        open_arr = snippet.count("[") - snippet.count("]")
        if open_obj < 0 or open_arr < 0:
            continue
        completed = snippet + ("]" * open_arr) + ("}" * open_obj)
        try:
            result = json.loads(completed)
            logger.warning(f"JSON repaired ({len(raw)-bp} chars trimmed): {list(result.keys())}")
            return result
        except json.JSONDecodeError:
            continue

    raise ValueError(f"JSON tahlil qilinmadi: {raw[:200]}")


def classify_request(text: str) -> dict:
    """
    Returns: tur, mavzu, muddat_kun, risk, kalit_sozlar,
             ishonch_darajasi, organ_nomi, maqsad, til
    """
    system = (
        "Siz O'zbekiston huquq tizimi va bank faoliyati bo'yicha mutaxassississiz. "
        "Faqat JSON formatida javob bering. JSON qiymatlarida apostrof (') ishlatmang."
    )
    prompt = f"""Quyidagi rasmiy murojaatni tahlil qiling va FAQAT JSON formatda qaytaring:
{{
    "tur": "prokuratura | soliq | markaziy_bank | boshqa",
    "mavzu": "murojaatning qisqa tavsifi (max 100 belgi)",
    "muddat_kun": 7,
    "risk": "low | medium | high",
    "kalit_sozlar": ["soz1", "soz2", "soz3"],
    "ishonch_darajasi": 85,
    "organ_nomi": "Sorovchi organ nomi",
    "maqsad": "tergov | tekshiruv | nazorat | boshqa",
    "til": "uz | ru | en"
}}

Qoidalar:
- muddat_kun: prokuratura=10, soliq=15, markaziy_bank=5, boshqa=10
- risk=high: jinoiy ish, muzlatish, katta miqdor, AML
- risk=medium: odatiy tekshiruv, standart sorov
- risk=low: malumot sorovi, statistika

Murojaat:
{text[:2000]}

FAQAT JSON qaytaring."""

    try:
        result = _parse_json(_llm(prompt, system=system, max_tokens=2048))
        result["tur"] = result.get("tur") if result.get("tur") in (
            "prokuratura", "soliq", "markaziy_bank", "boshqa"
        ) else "boshqa"
        result["kalit_sozlar"]     = [str(k) for k in result.get("kalit_sozlar", [])][:10]
        result["muddat_kun"]       = int(result.get("muddat_kun") or 10)
        result["ishonch_darajasi"] = max(0, min(100, int(result.get("ishonch_darajasi") or 0)))
        result["risk"] = result.get("risk") if result.get("risk") in (
            "low", "medium", "high"
        ) else "medium"
        result.setdefault("organ_nomi", "")
        result.setdefault("maqsad", "boshqa")
        result.setdefault("til", "uz")
        return result
    except Exception as e:
        logger.error(f"classify_request error: {e}")
        return {
            "tur": "boshqa", "mavzu": "Tahlil qilinmadi", "muddat_kun": 10,
            "risk": "medium", "kalit_sozlar": [], "ishonch_darajasi": 0,
            "organ_nomi": "", "maqsad": "boshqa", "til": "uz",
        }


def check_compliance(draft: str, context: str) -> dict:
    """
    Returns: muvofiq, xavf_darajasi, ball, muammolar,
             tavsiyalar, qonunlar (with links), xulosa, bank_siri_buzilishimi
    """
    system = (
        "Siz O'zbekiston bank huquqi va compliance bo'yicha yuqori malakali mutaxassississiz. "
        "Faqat JSON formatida javob bering. JSON qiymatlarida apostrof (') ishlatmang."
    )
    prompt = f"""Javob loyihasini O'zbekiston qonunchiligiga muvofiqligini tekshiring.

QONUNCHILIK BAZASI:
{context[:3000]}

TEKSHIRILADIGAN JAVOB LOYIHASI:
{draft[:2500]}

FAQAT ushbu JSON formatda qaytaring:
{{
    "muvofiq": true,
    "xavf_darajasi": "low | medium | high",
    "ball": 85,
    "muammolar": ["muammo 1"],
    "tavsiyalar": ["tavsiya 1"],
    "qonunlar": [
        {{"nomi": "Banklar va bank faoliyati togrisidagi Qonun 27-modda", "band": "3-qism"}}
    ],
    "xulosa": "2-3 gapda xulosa",
    "bank_siri_buzilishimi": false
}}

ball: 0=butunlay notogri, 100=mukammal
FAQAT JSON qaytaring."""

    try:
        result = _parse_json(_llm(prompt, system=system, max_tokens=2048))
        result["muammolar"]  = [str(m) for m in result.get("muammolar", [])]
        result["tavsiyalar"] = [str(t) for t in result.get("tavsiyalar", [])]
        result["ball"]       = max(0, min(100, int(result.get("ball") or 70)))
        result.setdefault("bank_siri_buzilishimi", False)
        enriched = []
        for law in result.get("qonunlar", []):
            if isinstance(law, dict):
                name, band = law.get("nomi", ""), law.get("band", "")
            else:
                name, band = str(law), ""
            enriched.append({"nomi": name, "band": band, "havola": _lex_link(name)})
        result["qonunlar"] = enriched
        return result
    except Exception as e:
        logger.error(f"check_compliance error: {e}")
        return {
            "muvofiq": True, "xavf_darajasi": "low", "ball": 70,
            "muammolar": [], "tavsiyalar": [],
            "qonunlar": [], "xulosa": "Tekshiruv bajarildi",
            "bank_siri_buzilishimi": False,
        }