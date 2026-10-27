# Document Intelligence Pipeline with Evaluation

RAG over a 30-document corpus (PDF/DOCX/TXT) with hybrid retrieval
(keyword TF-IDF + vector search) and a cross-encoder reranking step.
Answers are extractive quotes with source citations. Two chunking
strategies are compared on a 52-question evaluation set.

## Results (summary)

| Strategy | hit@5 | hit@1 | Accuracy |
| --- | ---: | ---: | ---: |
| Fixed windows (150 chars, 25 overlap) | 1.000 | 1.000 | 0.865 |
| Sentence packs (max 500 chars) | 1.000 | 1.000 | **0.981** |

Sentence packing wins because it never splits a sentence: fixed windows
cut 7 long facts across window boundaries, while sentence packs lost
only one two-sentence fact at a pack boundary. Full analysis:
`REPORT.md`, `results/results_table.md`.

## Setup

```bash
python -m venv .venv
# Windows PowerShell (if activation is blocked, run this first):
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` carries a CPU-torch extra index line; on first run
the embedding and reranker models download from Hugging Face
(~170 MB total, cached afterwards).

## Usage

```bash
python scripts/make_corpus.py                    # rebuild corpus/
python -m src.cli ingest --strategy sentence     # build + save an index
python -m src.cli ask --strategy sentence "How many days of annual leave?"
python -m src.cli evaluate                       # both strategies -> results/
python -m pytest tests/ -q                       # 9 tests
```

## Layout

- `src/` — loaders, chunking, hybrid retrieval + reranker, QA, evaluation, CLI
- `scripts/make_corpus.py` — reproducible corpus generator
- `corpus/` — 30 documents: 8 PDF, 8 DOCX, 14 TXT
- `eval/eval_set.json` — 52 questions with gold answers and gold sources
- `results/` — results table, per-question CSVs, summary JSON
- `tests/` — pytest suite (chunking, loaders, metrics, end-to-end ask)

## Requirements checklist

| Portal requirement | Where it is |
| --- | --- |
| RAG over ≥ 20 documents (PDF/DOCX/TXT) | `corpus/` (30 docs), `src/loaders.py` |
| Hybrid retrieval (keyword + vector) | `src/retrieval.py` (TF-IDF + FAISS) |
| Reranking step | `src/retrieval.py` (cross-encoder) |
| Evaluation set ≥ 30 Q/A pairs | `eval/eval_set.json` (52 pairs) |
| Retrieval hit rate + answer correctness | `results/results_table.md` |
| Two chunking strategies compared, with why | `src/chunking.py`, `REPORT.md` |
| Answers cite sources | `src/qa.py` (extractive + citation) |
| Code, evaluation set, results table, README | this repo |
