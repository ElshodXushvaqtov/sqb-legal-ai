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
