"""Two chunking strategies, compared head to head.

Chunking runs over the whole document (units joined), not per page or
paragraph, because per-unit chunking on this corpus's short units made
both strategies produce identical chunks. Each chunk keeps the locator
of the unit where it starts, so citations stay precise.

fixed:    sliding character windows (150 chars, 25 overlap), cut back to
          the nearest word boundary so words are never split. Windows
          can cut a sentence in half, so a fact can be split across
          two chunks.
sentence: split into sentences first, then greedily pack whole sentences
          into chunks of at most 500 chars. Sentences are never split,
          so a fact expressed in one sentence always stays in one chunk.
"""

import re

from src.config import FIXED_OVERLAP, FIXED_SIZE, SENTENCE_MAX

_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+")


def fixed_spans(text, size=FIXED_SIZE, overlap=FIXED_OVERLAP):
    """Return [(start, end)] character windows over text."""
    spans = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        if end < n:
            # Back off to the last space so no word is cut in half.
            space = text.rfind(" ", start, end)
            if space > start:
                end = space
        if text[start:end].strip():
            spans.append((start, end))
        if end >= n:
            break
        start = end - overlap
    return spans


def sentence_spans(text, max_chars=SENTENCE_MAX):
    """Return [(start, end)] spans of whole-sentence packs."""
    sentences = [
        (m.start(), m.end()) for m in _SENTENCE_RE.finditer(text)
    ]
    # Any trailing text without terminal punctuation is its own sentence.
    if sentences:
        last_end = sentences[-1][1]
        tail = text[last_end:]
        stripped = tail.strip()
        if stripped:
            start = last_end + (len(tail) - len(tail.lstrip()))
            sentences.append((start, start + len(stripped)))
    elif text.strip():
        sentences = [(0, len(text))]
    spans, cur_start, cur_end = [], None, None
    for start, end in sentences:
        if cur_start is None:
            cur_start, cur_end = start, end
        elif end - cur_start > max_chars:
            spans.append((cur_start, cur_end))
            cur_start, cur_end = start, end
        else:
            cur_end = end
    if cur_start is not None:
        spans.append((cur_start, cur_end))
    return spans


def fixed_chunks(text, size=FIXED_SIZE, overlap=FIXED_OVERLAP):
    return [text[s:e].strip() for s, e in fixed_spans(text, size, overlap)]


def sentence_chunks(text, max_chars=SENTENCE_MAX):
    return [text[s:e].strip() for s, e in sentence_spans(text, max_chars)]


def chunk_document(doc, strategy):
    """Chunk one document. Returns a list of chunk dicts."""
    span_fn = fixed_spans if strategy == "fixed" else sentence_spans
    full_text = "\n\n".join(text for text, _ in doc["units"])
    # Character offset where each unit starts in the joined text.
    unit_spans = []
    offset = 0
    for text, locator in doc["units"]:
        unit_spans.append((offset, offset + len(text), locator))
        offset += len(text) + 2
    chunks = []
    for i, (start, end) in enumerate(span_fn(full_text)):
        locator = unit_spans[-1][2]
        for u_start, u_end, u_loc in unit_spans:
            if u_start <= start < u_end:
                locator = u_loc
                break
        piece = full_text[start:end].strip()
        if piece:
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
