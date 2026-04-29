"""
rag.py  –  bilim bazasi va javob generatsiyasi
HuggingFace embeddings (lokal, CPU) + FAISS + Google Gemini
"""
import os
import time
import logging
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

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


# Primary model for generation; fallback used if primary is overloaded
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini-2.5-flash")
FALLBACK_MODEL   = os.getenv("GENERATION_FALLBACK", "gemini-2.0-flash")


def build_knowledge_base(docs: list[str]):
    """Chunk docs, embed with local MiniLM, store in FAISS."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.create_documents(docs)
    logger.info(f"Embedding {len(chunks)} chunk(s) with MiniLM (CPU)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    store = FAISS.from_documents(chunks, embeddings)
    logger.info("FAISS vektorstore tayyor")
    return store


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

def _call_gemini(prompt: str, system: str = "", max_tokens: int = 2500, retries: int = 3) -> str:
    """Call Gemini with retry on 429/503 and automatic model fallback."""
    config = types.GenerateContentConfig(
        max_output_tokens=max_tokens,
        temperature=0.2,
        system_instruction=system if system else None,
        thinking_config=types.ThinkingConfig(thinking_budget=512),
    )

    # Try primary model first, then fallback
    models_to_try = [GENERATION_MODEL, FALLBACK_MODEL]

    for model in models_to_try:
        for attempt in range(retries):
            try:
                response = _get_client().models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                if model != GENERATION_MODEL:
                    logger.warning(f"Fallback model ishlatildi: {model}")
                return response.text.strip()
            except (genai_errors.ClientError, genai_errors.ServerError) as e:
                code = getattr(e, "code", 0) or 0
                retryable = code in (429, 503) or "UNAVAILABLE" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
                if retryable and attempt < retries - 1:
                    wait = _retry_wait(e)
                    logger.warning(f"RAG [{model}] xatosi ({code}), {wait}s kutilmoqda... (urinish {attempt+1}/{retries})")
                    time.sleep(wait)
                elif retryable:
                    # All retries exhausted for this model, try fallback
                    logger.warning(f"[{model}] barcha urinishlar tugadi, keyingi modelga o'tilmoqda...")
                    break
                else:
                    raise

    raise RuntimeError("Barcha modellar va urinishlar tugadi. Keyinroq qayta urinib ko'ring.")


def generate_response(murojaat_text: str, classification: dict, vectorstore) -> str:
    """
    RAG-based official reply drafting in Uzbek.
    1. Retrieves top-k semantically similar law chunks
    2. Asks Gemini to write a structured, legally grounded response
    """
    tur    = classification.get("tur", "boshqa")
    mavzu  = classification.get("mavzu", "")
    muddat = classification.get("muddat_kun", 10)
    risk   = classification.get("risk", "medium")
    organ  = classification.get("organ_nomi", "")
    maqsad = classification.get("maqsad", "")

    # Semantic retrieval
    similar = vectorstore.similarity_search(murojaat_text, k=5)
    context = "\n\n".join([f"[{i+1}] {d.page_content}" for i, d in enumerate(similar)])

    deadline_note = {
        "prokuratura":   f"Javob muddati: {muddat} ish kuni (JPK 178-modda bo'yicha)",
        "soliq":         f"Javob muddati: {muddat} ish kuni (Soliq Kodeksi 86-modda bo'yicha)",
        "markaziy_bank": f"Javob muddati: {muddat} ish kuni (Markaziy bank yo'riqnomasi bo'yicha)",
    }.get(tur, f"Javob muddati: {muddat} ish kuni")

    risk_note = {
        "high": (
            "YUQORI XAVF: Javobda bank siri, jinoiy javobgarlik va huquqiy cheklovlar "
            "alohida ta'kidlansin. Bosh yuridik maslahatchi ko'rib chiqishi tavsiya etilsin."
        ),
        "medium": "O'rtacha xavf: standart bank protseduralariga qat'iy rioya qiling.",
        "low":    "Past xavf: standart rasmiy javob tartibi.",
    }.get(risk, "")

    system = (
        "Siz O'zbekiston Sanoat Qurilish Banki (SQB) Yuridik Bo'limi bosh mutaxassississiz. "
        "Rasmiy hujjatlar, O'zbek bank qonunchiligi va rasmiy yozishmalar bo'yicha chuqur "
        "bilimga egasiz. Har doim professional, aniq va qonunga mos javoblar tayyorlaysiz."
    )

    prompt = f"""Quyidagi so'rov ma'lumotlari va qonunchilik ko'chirmalariga asoslanib,
SQB banki nomidan RASMIY JAVOB LOYIHASINI tayyorlang.

{'='*50}
SO'ROV TAFSILOTLARI
{'='*50}
So'rov turi  : {tur.upper()}
So'rovchi    : {organ or "Ko'rsatilmagan"}
Mavzu        : {mavzu}
Maqsad       : {maqsad}
{deadline_note}
{risk_note}

{'='*50}
QONUNCHILIK BAZASI (tegishli bo'limlar)
{'='*50}
{context}

{'='*50}
MUROJAAT MATNI
{'='*50}
{murojaat_text[:2000]}

{'='*50}
JAVOB TALABLARI
{'='*50}
Javob quyidagi MAJBURIY tuzilmada bo'lsin:

1. KIRISH
- Murojaatni qabul qilinganligini tasdiqlash
- So'rovchi organ va murojaat sanasiga havola

2. HUQUQIY ASOS
- Javob berilayotgan aniq qonun moddalari (raqam va band bilan)
- Bank majburiyati yoki vakolati asosi

3. ASOSIY QISM
- So'ralgan ma'lumot yoki tushuntirish
- Bank siri doirasida taqdim etilishi mumkin bo'lgan ma'lumotlar
- Taqdim etilishi MUMKIN BO'LMAGAN ma'lumotlar (agar mavjud)

4. MUDDAT VA TARTIB
- Ma'lumot qachon va qanday shaklda taqdim etilishi

5. XULOSA
- Hamkorlikka tayyorlik
- Yuridik bo'lim aloqa ma'lumotlari

Uslub: rasmiy O'zbek tili, yuridik terminologiya, kamida 5 paragraf.
"""

    try:
        result = _call_gemini(prompt, system=system, max_tokens=4000)
        logger.info(f"Javob generatsiya muvaffaqiyatli: {len(result)} belgi")
        return result
    except Exception as e:
        logger.error(f"generate_response error: {e}")
        return (
            f"[TEXNIK XATOLIK: Javob generatsiyasida muammo yuz berdi]\n\n"
            f"Xato: {e}\n\n"
            "Iltimos, tizim ma'muriga murojaat qiling yoki keyinroq qayta urinib ko'ring."
        )