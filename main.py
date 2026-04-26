import os
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import tempfile
from dotenv import load_dotenv

from src.parser import extract_text
from src.classifier import classify_request, check_compliance
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

vectorstore = build_knowledge_base(LEGAL_DOCS)
requests_db = []

@app.get("/")
def root():
    return {"status": "SQB Legal AI ishlayapti"}

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse("static/index.html")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    suffix = ".pdf" if file.filename.endswith(".pdf") else ".docx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        text = extract_text(tmp_path)
    finally:
        os.unlink(tmp_path)

    print(f"✅ Text extracted: {len(text)} chars")

    classification = classify_request(text)
    print(f"✅ Classified: {classification}")


    docs = vectorstore.similarity_search(text, k=3)
    relevant_laws_context = "\n".join([doc.page_content for doc in docs])


    draft = generate_response(text, classification, vectorstore)
    print(f"✅ Draft generated: {len(draft)} chars")


    compliance = check_compliance(draft, relevant_laws_context)
    print(f"✅ Compliance checked: {compliance}")
    # ------------------------------

    request_id = str(uuid.uuid4())[:8]
    entry = {
        "id": request_id,
        "filename": file.filename,
        "text": text[:500],
        "classification": classification,
        "draft_response": draft,
        "compliance": compliance,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "approved_at": None,
        "edited_response": None
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

@app.post("/requests/{request_id}/edit")
async def edit_request(request_id: str, request: Request):
    body = await request.json()
    for req in requests_db:
        if req["id"] == request_id:
            req["edited_response"] = body.get("text")
            return req
    raise HTTPException(status_code=404, detail="Topilmadi")

# Mount static LAST
app.mount("/static", StaticFiles(directory="static"), name="static")