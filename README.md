# SQB Legal AI 🏦

AI-powered legal response system for SQB Bank. Automates responses to official government requests (prokuratura, tax authorities, Central Bank) using RAG + Google Gemini.

## Demo
Upload a PDF government request → AI classifies it → generates legally-compliant Uzbek response → operator approves/rejects.

## Tech Stack
- FastAPI + Python 3.12
- Google Gemini (LLM)
- LangChain + FAISS (RAG)
- HuggingFace Embeddings
- Tailwind CSS

## Setup
```bash
pip install fastapi uvicorn langchain langchain-google-genai langchain-community langchain-text-splitters faiss-cpu pymupdf python-docx python-multipart google-generativeai python-dotenv sentence-transformers reportlab
```

Create `.env`:
Run:
```bash
uvicorn main:app --reload
```

Open: http://127.0.0.1:8000/dashboard

## Features
- PDF/DOCX upload and parsing
- AI classification (type, deadline, risk level)
- RAG-based response generation using Uzbek law knowledge base
- Human-in-the-loop approve/reject
- Audit trail
- Statistics dashboard

## API Endpoints
- `GET /` — health check
- `POST /upload` — upload document
- `GET /requests` — list all requests
- `POST /requests/{id}/approve` — approve
- `POST /requests/{id}/reject` — reject

## Knowledge Base
10 Uzbek legal documents including:
- Bank siri qonuni
- JPK 178-modda
- AML qonuni
- Soliq kodeksi 86-modda
- Markaziy bank yo'riqnomasi
