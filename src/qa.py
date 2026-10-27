"""Extractive question answering: the answer is the best chunk itself,
quoted with its source citation. No generative model is involved, so an
answer can never invent a fact that is not in the corpus.
"""

from src.config import RETRIEVE_K, TOP_K


def cite(chunk):
    return f"{chunk['doc_id']} [{chunk['locator']}]"


def ask(question, index, reranker, top_k=TOP_K, retrieve_k=RETRIEVE_K):
    candidates = index.search(question, top_k=retrieve_k)
    ranked = reranker.rerank(question, candidates)
    top = ranked[:top_k]
    best = top[0][0] if top else None
    return {
        "question": question,
        "answer": best["text"] if best else "",
        "citation": cite(best) if best else "",
        "source_doc": best["doc_id"] if best else "",
        "results": [
            {"doc_id": c["doc_id"], "citation": cite(c), "text": c["text"]}
            for c, _ in top
        ],
    }
