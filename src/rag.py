import os
import vertexai
from langchain_google_vertexai import VertexAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = "sqb-ai-response-system"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)


def build_knowledge_base(docs: list[str]):

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.create_documents(docs)


    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore


def generate_response(murojaat_text: str, classification: dict, vectorstore) -> str:

    llm = VertexAI(
        model_name="gemini-2.5-flash",
        temperature=0.2,
        project=PROJECT_ID,
        location=LOCATION
    )


    docs = vectorstore.similarity_search(murojaat_text, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
    Siz SQB banki yuridik bo'limi xodimisiz. 
    Quyidagi qonunchilik va murojaat ma'lumotlari asosida rasmiy javob loyihasini tayyorlang.

    Qonunchilik bazasi:
    {context}

    Murojaat ma'lumotlari:
    - Turi: {classification.get('tur')}
    - Mavzu: {classification.get('mavzu')}

    Murojaat matni:
    {murojaat_text[:500]}

    Rasmiy, professional, O'zbek tilida kamida 3 paragraf javob yozing.
    """

    try:
        return llm.invoke(prompt)
    except Exception as e:
        return f"Javob tayyorlashda texnik xatolik: {str(e)}"