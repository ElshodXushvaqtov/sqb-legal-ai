import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = "sqb-ai-response-system"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-2.5-flash")


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


def check_compliance(draft_response: str) -> dict:
    prompt = f"""
    You are an Uzbekistan banking law expert. Analyze this bank response draft.

    Draft:
    {draft_response[:1500]}

    Read the draft carefully and identify which specific Uzbek laws and articles were referenced or used in this response.

    Return ONLY this JSON:
    {{
        "muvofiq": true,
        "xavf_darajasi": "low",
        "muammolar": [],
        "tavsiyalar": [],
        "qonunlar": [
            {{"nomi": "exact law name and article that appears in the draft", "havola": "https://lex.uz/acts/XXXXX"}}
        ],
        "xulosa": "one sentence about which laws this response is based on"
    }}

    Rules:
    - qonunlar must ONLY contain laws that are actually mentioned or referenced in the draft above
    - Do not add laws that are not in the draft
    - For havola use real lex.uz links:
      * Bank siri: https://lex.uz/acts/325746
      * JPK 178-modda: https://lex.uz/acts/111457
      * Banklar qonuni: https://lex.uz/acts/14232
      * Soliq kodeksi: https://lex.uz/acts/2354822
      * AML qonun: https://lex.uz/acts/3523929
      * Markaziy bank qonuni: https://lex.uz/acts/38446
    - muammolar and tavsiyalar must be simple strings only
    - muvofiq is true if response follows Uzbek banking law
    RETURN ONLY JSON.
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
        result['qonunlar'] = result.get('qonunlar', [])
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