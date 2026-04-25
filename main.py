import os
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse  # <-- Added this import
import tempfile
from dotenv import load_dotenv

from src.parser import extract_text
from src.classifier import classify_request
from src.rag import build_knowledge_base, generate_response
from data.knowledge_base import LEGAL_DOCS

load_dotenv()

app = FastAPI(title="SQB Legal AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NEW: Mount the static folder and create the dashboard route ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse("static/index.html")
# -------------------------------------------------------------------

# Build knowledge base on startup
vectorstore = build_knowledge_base(LEGAL_DOCS)

# In-memory storage for requests
requests_db = []

@app.get("/")
def root():
    return {"status": "SQB Legal AI ishlayapti"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Save temp file
    suffix = ".pdf" if file.filename.endswith(".pdf") else ".docx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Extract text
    text = extract_text(tmp_path)
    os.unlink(tmp_path)

    # Classify
    classification = classify_request(text)

    # Generate response
    draft = generate_response(text, classification, vectorstore)

    # Save to db
    request_id = str(uuid.uuid4())[:8]
    entry = {
        "id": request_id,
        "filename": file.filename,
        "text": text[:500],
        "classification": classification,
        "draft_response": draft,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "approved_at": None
    }
    requests_db.append(entry)

    return entry

@app.get("/requests")
def get_requests():
    return requests_db

@app.post("/requests/{request_id}/approve")
def approve_request(request_id: str):
    for req in requests_db:
        if req["id"] == request_id:
            req["status"] = "approved"
            req["approved_at"] = datetime.now().isoformat()
            return req
    raise HTTPException(status_code=404, detail="Topilmadi")

@app.post("/requests/{request_id}/reject")
def reject_request(request_id: str):
    for req in requests_db:
        if req["id"] == request_id:
            req["status"] = "rejected"
            req["approved_at"] = datetime.now().isoformat()
            return req
    raise HTTPException(status_code=404, detail="Topilmadi")