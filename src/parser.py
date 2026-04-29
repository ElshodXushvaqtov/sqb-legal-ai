import re
import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _clean(text: str) -> str:
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    # Remove lone page numbers
    text = re.sub(r"(?m)^\s*\d{1,3}\s*$", "", text)
    return text.strip()


def extract_text_from_bytes(data: bytes, suffix: str) -> str:
    suffix = suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf_bytes(data)
    elif suffix == ".docx":
        return _extract_docx_bytes(data)
    else:
        raise ValueError(
            f"Qo'llab-quvvatlanmaydigan format: '{suffix}'. Faqat .pdf yoki .docx."
        )


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    data = path.read_bytes()
    return extract_text_from_bytes(data, path.suffix)


def _extract_pdf_bytes(data: bytes) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError(
            "PyMuPDF o'rnatilmagan. Bajaring: pip install pymupdf"
        )

    doc = fitz.open(stream=data, filetype="pdf")
    parts: list[str] = []

    for page in doc:
        blocks = page.get_text("blocks")
        page_text = ""
        for block in sorted(blocks, key=lambda b: (b[1], b[0])):
            if block[6] == 0:  # text block (not image)
                page_text += block[4] + "\n"
        if page_text.strip():
            parts.append(page_text)

    doc.close()
    result = _clean("\n\n".join(parts))
    logger.debug(f"PDF matn ajratildi: {len(result):,} belgi")
    return result


def _extract_docx_bytes(data: bytes) -> str:
    try:
        from docx import Document
        from docx.oxml.ns import qn
    except ImportError:
        raise RuntimeError(
            "python-docx o'rnatilmagan. Bajaring: pip install python-docx"
        )

    doc = Document(io.BytesIO(data))
    parts: list[str] = []

    for element in doc.element.body:
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

        if tag == "p":
            text = "".join(run.text for run in element.iter(qn("w:t")))
            if text.strip():
                parts.append(text.strip())

        elif tag == "tbl":
            rows: list[str] = []
            for row in element.iter(qn("w:tr")):
                cells: list[str] = []
                for cell in row.iter(qn("w:tc")):
                    cell_text = " ".join(
                        "".join(run.text for run in para.iter(qn("w:t")))
                        for para in cell.iter(qn("w:p"))
                    ).strip()
                    cells.append(cell_text)
                rows.append(" | ".join(cells))
            if rows:
                parts.append("\n".join(rows))

    result = _clean("\n\n".join(parts))
    logger.debug(f"DOCX matn ajratildi: {len(result):,} belgi")
    return result