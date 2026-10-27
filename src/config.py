# Document Intelligence Pipeline with Evaluation
# (Varolline internship project 7)
#
# RAG over a 24-document corpus (PDF/DOCX/TXT) with hybrid retrieval
# (keyword TF-IDF + vector search) and a cross-encoder reranking step.
# Two chunking strategies are compared on the same 36-question
# evaluation set: fixed-size windows vs sentence-aware packing.
# Answers are extractive and always carry a source citation.

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = PROJECT_ROOT / "corpus"
INDEX_DIR = PROJECT_ROOT / "indexes"
EVAL_PATH = PROJECT_ROOT / "eval" / "eval_set.json"
RESULTS_DIR = PROJECT_ROOT / "results"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"

# Chunking: fixed windows are deliberately smaller than sentence packs,
# so the two strategies genuinely differ (see REPORT.md).
FIXED_SIZE = 150
FIXED_OVERLAP = 25
SENTENCE_MAX = 500

# Retrieval
RETRIEVE_K = 20      # candidates pulled by hybrid search before reranking
TOP_K = 5            # final results shown / used for hit@5
HYBRID_ALPHA = 0.5   # weight of vector score in the hybrid fusion
