"""Load PDF, DOCX and TXT documents into citable text units.

A unit is one page (PDF) or one paragraph (DOCX/TXT). Every unit keeps
its document id and a locator, so every answer can cite its source
precisely, e.g. ``leave_policy [p. 1]`` or ``moon_landing [para 3]``.
"""

from pathlib import Path

from pypdf import PdfReader
from docx import Document


def _iter_files(corpus_dir):
    for path in sorted(Path(corpus_dir).iterdir()):
        if path.suffix.lower() in (".pdf", ".docx", ".txt"):
            yield path


def load_document(path):
    """Return a list of (text, locator) units for one file."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        units = []
        for i, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                units.append((text, f"p. {i}"))
        return units
    if suffix == ".docx":
        doc = Document(str(path))
        units = []
        for i, para in enumerate(doc.paragraphs, start=1):
            text = para.text.strip()
            if text:
                units.append((text, f"para {i}"))
        return units
    if suffix == ".txt":
        text = path.read_text(encoding="utf-8")
        units = []
        for i, block in enumerate(text.split("\n\n"), start=1):
            block = block.strip()
            if block:
                units.append((block, f"para {i}"))
        return units
    raise ValueError(f"Unsupported file type: {path}")


def load_corpus(corpus_dir):
    """Return a list of docs: {doc_id, path, units}."""
    docs = []
    for path in _iter_files(corpus_dir):
        docs.append({
            "doc_id": path.stem,
            "path": str(path),
            "units": load_document(path),
        })
    return docs
