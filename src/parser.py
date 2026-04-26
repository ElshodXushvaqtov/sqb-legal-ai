import fitz
from docx import Document

def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    else:
        raise ValueError("Faqat PDF yoki DOCX fayllar qabul qilinadi")