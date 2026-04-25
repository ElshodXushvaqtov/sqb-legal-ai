import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv()

# Use your project's text ID and confirmed region
PROJECT_ID = "sqb-ai-response-system"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Updated to use the 2.5 series visible in your Model Garden
model = GenerativeModel("gemini-2.5-flash")


def classify_request(text: str) -> dict:
    prompt = f"""
    Analyze the following official request and return ONLY a JSON object:
    {{
        "tur": "prokuratura | soliq | markaziy_bank | boshqa",
        "mavzu": "short description of the request",
        "muddat_kun": 7,
        "risk": "low | medium | high",
        "kalit_sozlar": ["keyword1", "keyword2"]
    }}

    Request text:
    {text[:1000]}

    RETURN ONLY JSON. DO NOT INCLUDE MARKDOWN BLOCKS.
    """

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Robust JSON extraction
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        return json.loads(raw)
    except Exception as e:
        print(f"Classification Error: {e}")
        return {
            "tur": "boshqa",
            "mavzu": "Error in AI analysis",
            "muddat_kun": 10,
            "risk": "medium",
            "kalit_sozlar": []
        }