"""Hybrid retrieval (vector + keyword) with a cross-encoder reranker.

Vector search: all-MiniLM-L6-v2 embeddings in a FAISS IndexFlatIP
(cosine similarity on L2-normalised vectors).
Keyword search: TF-IDF cosine over the same chunks.
Hybrid fusion: both score lists are min-max normalised to [0, 1] and
combined as alpha * vector + (1 - alpha) * keyword.
Reranking: a cross-encoder scores (question, chunk) pairs jointly and
reorders the top candidates. If the cross-encoder model cannot be
loaded, reranking falls back to the hybrid order and reports that.
"""

import os
import pickle

import faiss
import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import EMBED_MODEL, HYBRID_ALPHA, RERANK_MODEL, RETRIEVE_K


def _min_max(scores):
    scores = np.asarray(scores, dtype=float)
    lo, hi = scores.min(), scores.max()
    if hi <= lo:
        return np.zeros_like(scores)
    return (scores - lo) / (hi - lo)


class Index:
    def __init__(self, chunks, embed_model=EMBED_MODEL):
        self.chunks = chunks
        texts = [c["text"] for c in chunks]
        self.embedder = SentenceTransformer(embed_model)
        embeddings = self.embedder.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.faiss_index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.faiss_index.add(self.embeddings)
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def search(self, query, top_k=RETRIEVE_K, alpha=HYBRID_ALPHA):
        """Return [(chunk, hybrid_score)] for the top_k candidates."""
        q_vec = self.embedder.encode(
            [query], normalize_embeddings=True, show_progress_bar=False
        ).astype(np.float32)
        vec_scores, vec_idx = self.faiss_index.search(q_vec, len(self.chunks))
        vec_scores = _min_max(vec_scores[0])
        q_tfidf = self.vectorizer.transform([query])
        kw_scores = cosine_similarity(q_tfidf, self.tfidf_matrix)[0]
        kw_scores = _min_max(kw_scores)
        hybrid = alpha * vec_scores + (1 - alpha) * kw_scores
        order = np.argsort(-hybrid)[:top_k]
        return [(self.chunks[i], float(hybrid[i])) for i in order]

    def save(self, directory):
        directory.mkdir(parents=True, exist_ok=True)
        import json
        (directory / "chunks.json").write_text(
            json.dumps(self.chunks), encoding="utf-8"
        )
        faiss.write_index(self.faiss_index, str(directory / "faiss.index"))
        with open(directory / "tfidf.pkl", "wb") as f:
            pickle.dump((self.vectorizer, self.tfidf_matrix), f)
        np.save(directory / "embeddings.npy", self.embeddings)

    @classmethod
    def load(cls, directory, chunks=None):
        import json
        obj = cls.__new__(cls)
        obj.chunks = chunks if chunks is not None else json.loads(
            (directory / "chunks.json").read_text(encoding="utf-8")
        )
        obj.embedder = SentenceTransformer(EMBED_MODEL)
        obj.embeddings = np.load(directory / "embeddings.npy")
        obj.faiss_index = faiss.read_index(str(directory / "faiss.index"))
        with open(directory / "tfidf.pkl", "rb") as f:
            obj.vectorizer, obj.tfidf_matrix = pickle.load(f)
        return obj


class Reranker:
    def __init__(self, model_name=None):
        # A local directory with the model files can be used instead of
        # the Hub id, e.g. DOCINT_RERANK_MODEL=models/cross-encoder.
        model_name = model_name or os.environ.get(
            "DOCINT_RERANK_MODEL", RERANK_MODEL
        )
        try:
            self.model = CrossEncoder(model_name)
            self.available = True
        except Exception:
            self.model = None
            self.available = False

    def rerank(self, query, candidates):
        """Reorder [(chunk, score)] by cross-encoder relevance."""
        if not self.available or not candidates:
            return candidates
        pairs = [(query, chunk["text"]) for chunk, _ in candidates]
        scores = self.model.predict(pairs, show_progress_bar=False)
        order = np.argsort(-np.asarray(scores))
        return [(candidates[i][0], float(scores[i])) for i in order]
