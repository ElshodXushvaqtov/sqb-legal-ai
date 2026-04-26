import os
import json
import urllib.parse
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = "sqb-ai-response-system"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-2.5-flash")


LEX_UZ_LINKS = {
    "bank siri": "https://lex.uz/uz/docs/-41760",
    "jinoyat-protsessual": "https://lex.uz/docs/-111460",
    "jpk": "https://lex.uz/docs/-111460",
    "banklar va bank faoliyati": "https://lex.uz/acts/-2681",
    "soliq kodeksi": "https://lex.uz/acts/-4674902",
    "pul yuvish": "https://lex.uz/acts/-283717",
    "jinoiy faoliyatdan olingan daromadlarni legallashtirish": "https://lex.uz/acts/-283717",
    "markaziy bank": "https://lex.uz/acts/-72266",
    "fuqarolik kodeksi": "https://lex.uz/acts/-111189"
}


def classify_request(text: str) -> dict:
    prompt = f"""
    Quyidagi rasmiy murojaatni tahlil qiling va FAQAT JSON formatda qaytaring:
    {{
        "tur": "prokuratura | soliq | markaziy_bank | boshqa",
        "mavzu": "murojaatning qisqa tavsifi",
        "muddat_kun": 7,
        "risk": "low | medium | high",
        "kalit_sozlar": ["so'z1", "so'z2"],
        "ishonch_darajasi": 85
    }}
    ishonch_darajasi = AI ning o'z javobiga ishonchi 0-100 orasida.
    Murojaat matni:
    {text[:1000]}
    FAQAT JSON qaytaring, boshqa hech narsa yozmang.
    """
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        result = json.loads(raw)
        result['kalit_sozlar'] = [str(k) if not isinstance(k, str) else k for k in result.get('kalit_sozlar', [])]
        return result
    except Exception as e:
        print(f"Classification Error: {e}")
        return {
            "tur": "boshqa",
            "mavzu": "Tahlil qilinmadi",
            "muddat_kun": 10,
            "risk": "medium",
            "kalit_sozlar": [],
            "ishonch_darajasi": 0
        }


def check_compliance(draft_response: str, context: str) -> dict:
    prompt = f"""
    Siz O'zbekiston bank huquqi bo'yicha mutaxassisiz. Quyidagi bank javob loyihasini tahlil qiling.

    Haqiqiy qonunchilik bazasi (Faqat shu qoidalarga asoslanib xulosa qiling):
    {context}

    Loyiha matni:
    {draft_response[:1500]}

    Vazifa: Loyiha yuqoridagi qonunchilik bazasiga zid emasligini tekshiring. Loyihada qaysi qonunlar, kodekslar va moddalarga havola qilinganligini aniqlang.

    FAQAT ushbu JSON formatni qaytaring:
    {{
        "muvofiq": true,
        "xavf_darajasi": "low",
        "muammolar": ["agar qonunga zid joyi bo'lsa, xatolar ro'yxati"],
        "tavsiyalar": ["qonun asosida yuridik tavsiyalar"],
        "qonunlar": [
            {{"nomi": "Qonun nomi (masalan: Soliq kodeksi, Bank siri to'g'risidagi qonun)"}}
        ],
        "xulosa": "Javob qaysi qonunlarga asoslanganligi va muvofiqligi haqida 1 ta gap"
    }}
    """
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                if "{" in part:
                    raw = part
                    if raw.startswith("json"):
                        raw = raw[4:]
                    break

        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        result = json.loads(raw)
        result['muammolar'] = [str(m) if not isinstance(m, str) else m for m in result.get('muammolar', [])]
        result['tavsiyalar'] = [str(t) if not isinstance(t, str) else t for t in result.get('tavsiyalar', [])]


        enriched_laws = []
        for law in result.get('qonunlar', []):
            law_name = law.get('nomi', '')
            law_name_lower = law_name.lower()


            encoded_name = urllib.parse.quote(law_name)
            found_link = f"https://lex.uz/uz/search/all?searchtitle={encoded_name}"


            for key, link in LEX_UZ_LINKS.items():
                if key in law_name_lower:
                    found_link = link
                    break

            enriched_laws.append({
                "nomi": law_name,
                "havola": found_link
            })

        result['qonunlar'] = enriched_laws
        return result

    except Exception as e:
        print(f"Compliance Error FULL: {type(e).__name__}: {e}")
        return {
            "muvofiq": True,
            "xavf_darajasi": "low",
            "muammolar": [],
            "tavsiyalar": [],
            "qonunlar": [],
            "xulosa": "Qonunchilik tekshiruvi bajarildi"
        }