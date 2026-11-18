from pathlib import Path
import re
from pypdf import PdfReader
from docx import Document
from sqlalchemy.orm import Session
from ..database import DocumentChunk
from ..config import ROOT

KB = ROOT / "knowledge_base"

def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf": return "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    if suffix == ".docx": return "\n".join(p.text for p in Document(str(path)).paragraphs)
    if suffix == ".txt": return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError("Only PDF, DOCX and TXT files are supported")

def ingest(path: Path, db: Session, display_name: str | None = None) -> int:
    text = extract_text(path)
    # Character-based overlapping chunks preserve Bangla Unicode safely.
    chunks = [text[i:i+1200] for i in range(0, len(text), 1000) if text[i:i+1200].strip()]
    for chunk in chunks:
        db.add(DocumentChunk(filename=(display_name or path.name)[:255], content=chunk))
    db.commit()
    return len(chunks)

def _terms(value: str) -> set[str]:
    return {w.casefold() for w in re.findall(r"[\w\u0980-\u09FF]+", value) if len(w) > 1}

def retrieve(query: str, db: Session, limit: int = 4) -> str:
    terms = _terms(query)
    if not terms: return ""
    rows = db.query(DocumentChunk).all()
    scored = []
    for row in rows:
        content_terms = _terms(row.content)
        score = len(terms & content_terms) / max(1, len(terms))
        if score > 0: scored.append((score, row.content))
    scored.sort(key=lambda item: item[0], reverse=True)
    return "\n---\n".join(content for _, content in scored[:limit])
