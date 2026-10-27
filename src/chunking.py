"""Two chunking strategies, compared head to head.

fixed:    sliding character windows (150 chars, 25 overlap), cut back to
          the nearest word boundary so words are never split.
sentence: split into sentences first, then greedily pack whole sentences
          into chunks of at most 500 chars. Sentences are never split,
          so a fact expressed in one sentence always stays in one chunk.
"""

import re

from src.config import FIXED_OVERLAP, FIXED_SIZE, SENTENCE_MAX

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def fixed_chunks(text, size=FIXED_SIZE, overlap=FIXED_OVERLAP):
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        if end < n:
            # Back off to the last space so no word is cut in half.
            space = text.rfind(" ", start, end)
            if space > start:
                end = space
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break
        start = end - overlap
    return chunks


def sentence_chunks(text, max_chars=SENTENCE_MAX):
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    chunks, current = [], ""
    for sent in sentences:
        if current and len(current) + 1 + len(sent) > max_chars:
            chunks.append(current)
            current = sent
        else:
            current = f"{current} {sent}".strip() if current else sent
    if current:
        chunks.append(current)
    return chunks


def chunk_document(doc, strategy):
    """Chunk every unit of one doc. Returns a list of chunk dicts."""
    chunker = fixed_chunks if strategy == "fixed" else sentence_chunks
    chunks = []
    for text, locator in doc["units"]:
        for i, piece in enumerate(chunker(text)):
            chunks.append({
                "doc_id": doc["doc_id"],
                "locator": locator,
                "chunk_id": f"{doc['doc_id']}#{locator}#{i}",
                "text": piece,
            })
    return chunks


def chunk_corpus(docs, strategy):
    chunks = []
    for doc in docs:
        chunks.extend(chunk_document(doc, strategy))
    return chunks
