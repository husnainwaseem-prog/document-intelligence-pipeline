# Results table — Document Intelligence Pipeline with Evaluation

Evaluation set: 52 questions (`eval/eval_set.json`): 42 short-fact questions
plus 10 long-span questions whose gold answers are whole sentences or
two-sentence facts. Corpus: 30 documents (8 PDF, 8 DOCX, 14 TXT).
Retrieval for both strategies: hybrid TF-IDF + vector search (top 20),
then cross-encoder reranking (top 5). Metrics:

- **hit@5**: gold source document is among the top-5 results.
- **hit@1**: gold source document is the top result.
- **accuracy**: the gold answer phrase appears in the top-1 chunk
  (the quoted answer).
- **phrase survival**: the gold phrase appears in at least one chunk
  of the gold document, regardless of retrieval — a pure chunking
  metric.

| Strategy | Chunks | hit@5 | hit@1 | Accuracy | Phrase survival |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed windows (150 chars, 25 overlap) | 135 | 1.000 (52/52) | 1.000 (52/52) | 0.865 (45/52) | 0.865 (45/52) |
| Sentence packs (max 500 chars) | 45 | 1.000 (52/52) | 1.000 (52/52) | 0.981 (51/52) | 0.981 (51/52) |

## Which performs better, and why

**Sentence packing wins on accuracy, 0.981 vs 0.865.** Retrieval is
identical for both (hit@5 and hit@1 are 1.000 either way), so the
entire gap comes from chunking: accuracy equals phrase survival for
both strategies, meaning whenever a gold phrase survived chunking, the
pipeline retrieved it and ranked it first.

Fixed windows failed 7 questions (q43, q45, q46, q47, q49, q50, q52):
every one is a long-span question whose gold answer is 86–155
characters long and was cut across a 150-char window boundary. All 42
short-fact questions passed under both strategies, because the
word-boundary backoff plus 25-char overlap protects short phrases.

Sentence packing failed only q46: the two-sentence heart-chambers fact
fell across a pack boundary, showing sentence packing reduces split
facts but does not eliminate them entirely.

Per-question detail: `per_question_fixed.csv`, `per_question_sentence.csv`.
