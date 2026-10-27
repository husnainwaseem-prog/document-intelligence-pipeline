# Report — Document Intelligence Pipeline with Evaluation

## Task

Build a RAG system over a corpus of at least 20 documents (PDF/DOCX/TXT)
using hybrid retrieval (keyword and vector search) with a reranking step,
evaluate it on at least 30 question-answer pairs measuring retrieval hit
rate and answer correctness, compare at least two chunking strategies and
report which performs better and why, and cite sources in answers.

## Corpus

30 documents, generated reproducibly by `scripts/make_corpus.py`:

- 8 PDF, 8 DOCX, 14 TXT (24 core documents + 6 distractors).
- Core documents cover company policies, science, history, health, and
  technology, each with 4 fact-dense paragraphs.
- Distractors (`leave_around_world`, `heart_health`, `python_libraries`,
  `war_timeline`, `planet_exploration`, `ocean_pollution`) are topically
  close to real documents but contain none of the evaluation gold
  phrases, so they make retrieval work harder without making any
  question ambiguous.

## Pipeline

1. **Loaders** (`src/loaders.py`): pypdf per page, python-docx per
   paragraph, TXT per blank-line block. Every unit keeps its document
   id and locator, so every answer cites its source.
2. **Chunking** (`src/chunking.py`): whole-document chunking with two
   strategies — fixed windows (150 chars, 25 overlap, cut back to word
   boundaries) and sentence packs (whole sentences packed to max
   500 chars). Each chunk records the locator of the unit it starts in.
3. **Hybrid retrieval** (`src/retrieval.py`): all-MiniLM-L6-v2 embeddings
   in a FAISS index plus TF-IDF keyword search; both scores are
   min-max normalised and fused 50/50; top 20 candidates pass on.
4. **Reranking**: cross-encoder `ms-marco-MiniLM-L6-v2` scores
   (question, chunk) pairs and reorders the candidates; top 5 are kept.
   If the model cannot load, reranking falls back to hybrid order
   (this did not happen in the reported run).
5. **Answering** (`src/qa.py`): extractive — the top-1 chunk is quoted
   with its citation (`doc_id [locator]`). No generative model is
   involved, so an answer cannot invent a fact outside the corpus.

## Evaluation method

`eval/eval_set.json` holds 52 questions, each with a gold answer phrase
and a gold source document: 42 short-fact questions and 10 long-span
questions whose gold answers are whole sentences or two-sentence facts.
Metrics: hit@5, hit@1, accuracy (gold phrase in the top-1 chunk), and
phrase survival (gold phrase in any chunk of the gold document).

## Results

| Strategy | Chunks | hit@5 | hit@1 | Accuracy | Phrase survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed windows (150/25) | 135 | 1.000 | 1.000 | 0.865 | 0.865 |
| Sentence packs (≤500) | 45 | 1.000 | 1.000 | 0.981 | 0.981 |

Full table and per-question rows: `results/results_table.md`,
`results/per_question_fixed.csv`, `results/per_question_sentence.csv`.

## Comparison: which is better, and why

**Sentence packing is better, 0.981 vs 0.865 accuracy.** The gap is
entirely a chunking effect, not a retrieval effect: hit@5 and hit@1 are
1.000 for both strategies, and accuracy equals phrase survival for
both, so whenever a gold phrase survived chunking, hybrid search plus
the cross-encoder found it and ranked it first.

Fixed windows failed 7 questions (q43, q45, q46, q47, q49, q50, q52) —
all long-span questions whose 86–155 character gold answers were cut
across a 150-char window boundary. All 42 short-fact questions passed
under both strategies: the word-boundary backoff plus 25-char overlap
protects short phrases. Sentence packing failed only q46, where a
two-sentence fact fell across a pack boundary — sentence awareness
reduces split facts sharply but does not eliminate them.

## Limitations (honest)

- Small synthetic corpus with distinctive facts; retrieval scores of
  1.000 will not transfer to a large, messy, real-world corpus.
- Correctness is strict phrase containment, with no partial credit for
  paraphrases; answers are extractive quotes, not generated prose.
- English only; the reranker model (~90 MB) downloads on first run.
- Chunk sizes differ between strategies (150 vs ≤500 chars), so the
  comparison measures the strategies as configured, not size-matched
  variants.

## Reproduction

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
python scripts/make_corpus.py     # rebuild the 30-document corpus
python -m src.cli evaluate        # both strategies, writes results/
python -m pytest tests/ -q        # 9 tests
```

To use a local reranker copy instead of the Hub download:
`DOCINT_RERANK_MODEL=models/cross-encoder python -m src.cli evaluate`.
