"""
main.py  –  SQB Legal AI v3.0
FastAPI entry-point: file upload, request lifecycle, stats.
"""
import os
import uuid
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

from src.parser import extract_text_from_bytes
from src.classifier import classify_request, check_compliance
from src.rag import build_knowledge_base, generate_response
from data.knowledge_base import LEGAL_DOCS

load_dotenv()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ── DB helpers ───────────────────────────────────────────────────────────────
DB_PATH = Path("data/requests_db.json")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
_db_lock = asyncio.Lock()

def load_db() -> list:
    if DB_PATH.exists():
        try:
            text = DB_PATH.read_text(encoding="utf-8").strip()
            return json.loads(text) if text else []
        except Exception as e:
            logger.error(f"DB load error: {e}")
            return []
    return []

async def save_db(data: list):
    async with _db_lock:
        DB_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

requests_db: list = load_db()

# ── Lifespan: build vectorstore once ─────────────────────────────────────────
vectorstore = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global vectorstore
    logger.info("Bilim bazasi qurilmoqda...")
    vectorstore = build_knowledge_base(LEGAL_DOCS)
    logger.info(f"Bilim bazasi tayyor — {len(LEGAL_DOCS)} hujjat yuklandi")
    yield
    logger.info("Server to'xtatilmoqda")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SQB Legal AI",
    version="3.0",
    description="Rasmiy hujjatlarni tahlil qilish va javob tayyorlash tizimi",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Optional API-key auth (set API_KEY in .env to enable) ────────────────────
_API_KEY = os.getenv("API_KEY", "")
security = HTTPBearer(auto_error=False)

def verify_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not _API_KEY:
        return  # auth disabled
    if not credentials or credentials.credentials != _API_KEY:
        raise HTTPException(status_code=401, detail="Avtorizatsiya talab etiladi")

# ── File validation ───────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))

def validate_file(filename: str, size_bytes: int):
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400, f"Faqat PDF yoki DOCX fayllar qabul qilinadi. Yuborildi: {suffix}"
        )
    if size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"Fayl hajmi {MAX_FILE_SIZE_MB} MB dan oshmasligi kerak")

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "version": "3.0",
        "requests_count": len(requests_db),
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/", tags=["System"])
def root():
    return {"status": "SQB Legal AI v3.0 ishlayapti"}

@app.get("/dashboard", include_in_schema=False)
async def get_dashboard():
    index = Path("static/index.html")
    if not index.exists():
        raise HTTPException(404, "Frontend qurilmagan. 'static/index.html' topilmadi.")
    return FileResponse(str(index))


@app.post("/upload", tags=["Documents"], dependencies=[Depends(verify_key)])
async def upload_document(file: UploadFile = File(...)):
    """
    PDF yoki DOCX hujjatni qabul qiladi, tahlil qiladi va javob loyihasini qaytaradi.
    """
    content = await file.read()
    validate_file(file.filename, len(content))
    logger.info(f"Fayl qabul qilindi: {file.filename} ({len(content):,} bayt)")

    suffix = Path(file.filename).suffix.lower()
    try:
        # Pass raw bytes in-memory — no temp file, avoids all file-handle issues
        text = extract_text_from_bytes(content, suffix)
    except Exception as e:
        logger.error(f"Matn ajratish xatosi ({file.filename}): {e}")
        raise HTTPException(422, f"Matnni o'qishda xatolik: {e}")

    if not text.strip():
        raise HTTPException(422, "Fayl bo'sh yoki matn topilmadi")

    logger.info(f"Matn ajratildi: {len(text):,} belgi")

    # ── Classification ────────────────────────────────────────────────────────
    classification = classify_request(text)
    logger.info(f"Tasniflandi: {classification.get('tur')} / risk={classification.get('risk')}")

    # ── RAG response generation ───────────────────────────────────────────────
    if vectorstore is None:
        raise HTTPException(503, "Bilim bazasi hali tayyorlanmadi, qayta urinib ko'ring")

    draft = generate_response(text, classification, vectorstore)
    logger.info(f"Javob tayyorlandi: {len(draft):,} belgi")

    # ── Compliance check ──────────────────────────────────────────────────────
    similar_docs = vectorstore.similarity_search(text, k=3)
    context = "\n\n".join([d.page_content for d in similar_docs])
    compliance = check_compliance(draft, context)
    logger.info(f"Compliance: muvofiq={compliance.get('muvofiq')}, xavf={compliance.get('xavf_darajasi')}")

    # ── Persist ───────────────────────────────────────────────────────────────
    entry = {
        "id": str(uuid.uuid4())[:8],
        "filename": file.filename,
        "text_preview": text[:1000],
        "full_text_length": len(text),
        "classification": classification,
        "draft_response": draft,
        "compliance": compliance,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "approved_at": None,
        "rejected_at": None,
        "edited_response": None,
        "editor_note": None,
        "edited_at": None,
    }
    requests_db.append(entry)
    await save_db(requests_db)
    return entry


@app.get("/requests", tags=["Requests"])
def get_requests(
    status: Optional[str] = Query(None, description="pending | approved | rejected"),
    tur: Optional[str] = Query(None, description="prokuratura | soliq | markaziy_bank | boshqa"),
    risk: Optional[str] = Query(None, description="low | medium | high"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    items = requests_db
    if status:
        items = [r for r in items if r.get("status") == status]
    if tur:
        items = [r for r in items if r.get("classification", {}).get("tur") == tur]
    if risk:
        items = [r for r in items if r.get("classification", {}).get("risk") == risk]
    # newest first
    items = sorted(items, key=lambda r: r.get("created_at", ""), reverse=True)
    total = len(items)
    return {"total": total, "items": items[offset: offset + limit]}


@app.get("/requests/{request_id}", tags=["Requests"])
def get_request(request_id: str):
    for req in requests_db:
        if req["id"] == request_id:
            return req
    raise HTTPException(404, "Murojaat topilmadi")


@app.post("/requests/{request_id}/approve", tags=["Requests"], dependencies=[Depends(verify_key)])
def approve_request(request_id: str):
    for req in requests_db:
        if req["id"] == request_id:
            if req["status"] != "pending":
                raise HTTPException(400, "Faqat kutilayotgan murojaatlarni tasdiqlash mumkin")
            req["status"] = "approved"
            req["approved_at"] = datetime.now().isoformat()
            asyncio.create_task(save_db(requests_db))  # non-blocking
            return req
    raise HTTPException(404, "Murojaat topilmadi")


@app.post("/requests/{request_id}/reject", tags=["Requests"], dependencies=[Depends(verify_key)])
def reject_request(request_id: str):
    for req in requests_db:
        if req["id"] == request_id:
            if req["status"] != "pending":
                raise HTTPException(400, "Faqat kutilayotgan murojaatlarni rad etish mumkin")
            req["status"] = "rejected"
            req["rejected_at"] = datetime.now().isoformat()   # ← BUG FIX: was approved_at
            asyncio.create_task(save_db(requests_db))
            return req
    raise HTTPException(404, "Murojaat topilmadi")


@app.post("/requests/{request_id}/edit", tags=["Requests"], dependencies=[Depends(verify_key)])
async def edit_request(request_id: str, request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Noto'g'ri JSON format")

    new_text = str(body.get("text", "")).strip()
    note = str(body.get("note", ""))[:500]  # limit note length
    if not new_text:
        raise HTTPException(400, "Matn bo'sh bo'lishi mumkin emas")
    if len(new_text) > 20_000:
        raise HTTPException(400, "Matn juda uzun (max 20,000 belgi)")

    for req in requests_db:
        if req["id"] == request_id:
            req["edited_response"] = new_text
            req["editor_note"] = note
            req["edited_at"] = datetime.now().isoformat()
            await save_db(requests_db)
            return req
    raise HTTPException(404, "Murojaat topilmadi")


@app.delete("/requests/{request_id}", tags=["Requests"], dependencies=[Depends(verify_key)])
async def delete_request(request_id: str):
    global requests_db
    before = len(requests_db)
    requests_db = [r for r in requests_db if r["id"] != request_id]
    if len(requests_db) == before:
        raise HTTPException(404, "Murojaat topilmadi")
    await save_db(requests_db)
    return {"deleted": request_id}


@app.get("/stats", tags=["Analytics"])
def get_stats():
    total = len(requests_db)
    pending  = sum(1 for r in requests_db if r["status"] == "pending")
    approved = sum(1 for r in requests_db if r["status"] == "approved")
    rejected = sum(1 for r in requests_db if r["status"] == "rejected")

    by_type: dict = {}
    by_risk: dict = {}
    avg_text_len = 0

    for r in requests_db:
        cl = r.get("classification", {})
        t  = cl.get("tur", "boshqa")
        rk = cl.get("risk", "low")
        by_type[t] = by_type.get(t, 0) + 1
        by_risk[rk] = by_risk.get(rk, 0) + 1
        avg_text_len += r.get("full_text_length", 0)

    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "approval_rate": round(approved / total * 100, 1) if total else 0,
        "by_type": by_type,
        "by_risk": by_risk,
        "avg_text_length": round(avg_text_len / total) if total else 0,
    }


# Mount static LAST (correct)
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")