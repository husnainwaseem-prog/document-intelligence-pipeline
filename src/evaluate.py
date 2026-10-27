"""Evaluation: retrieval hit rate and answer correctness, per chunking
strategy, on the same question set.

hit@5:      the gold source document appears among the top-5 results
            after hybrid retrieval + reranking.
correct:    the gold answer phrase (normalised) appears in the top-1
            chunk, i.e. the quoted answer actually contains the fact.
"""

import csv
import json
import re

from src.chunking import chunk_corpus
from src.config import RESULTS_DIR, TOP_K
from src.loaders import load_corpus
from src.qa import ask
from src.retrieval import Index, Reranker


def _norm(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def score_question(result, gold_doc, gold_answer):
    docs = [r["doc_id"] for r in result["results"]]
    hit = gold_doc in docs
    top1 = docs[0] == gold_doc if docs else False
    correct = _norm(gold_answer) in _norm(result["answer"])
    return hit, top1, correct


def evaluate_strategy(strategy, docs, eval_set, reranker):
    chunks = chunk_corpus(docs, strategy)
    index = Index(chunks)
    by_doc = {}
    for chunk in chunks:
        by_doc.setdefault(chunk["doc_id"], []).append(chunk["text"])
    rows = []
    for item in eval_set:
        result = ask(item["question"], index, reranker)
        hit, top1, correct = score_question(
            result, item["gold_doc"], item["gold_answer"]
        )
        # Pure chunking metric: does ANY chunk of the gold doc contain
        # the whole gold phrase, regardless of retrieval?
        survives = any(
            _norm(item["gold_answer"]) in _norm(t)
            for t in by_doc.get(item["gold_doc"], [])
        )
        rows.append({
            "id": item["id"],
            "question": item["question"],
            "gold_doc": item["gold_doc"],
            "gold_answer": item["gold_answer"],
            "predicted_doc": result["source_doc"],
            "citation": result["citation"],
            "hit@5": hit,
            "hit@1": top1,
            "correct": correct,
            "phrase_survives": survives,
        })
    n = len(rows)
    summary = {
        "strategy": strategy,
        "n_questions": n,
        "n_chunks": len(chunks),
        "hit_rate@5": sum(r["hit@5"] for r in rows) / n if n else 0.0,
        "hit_rate@1": sum(r["hit@1"] for r in rows) / n if n else 0.0,
        "accuracy": sum(r["correct"] for r in rows) / n if n else 0.0,
        "gold_phrase_survival": sum(
            r["phrase_survives"] for r in rows
        ) / n if n else 0.0,
        "reranker": "cross-encoder" if reranker.available else "hybrid-fallback",
    }
    return summary, rows


def run_evaluation(corpus_dir, eval_path, results_dir=RESULTS_DIR):
    docs = load_corpus(corpus_dir)
    eval_set = json.loads(open(eval_path, encoding="utf-8").read())
    reranker = Reranker()
    results_dir.mkdir(parents=True, exist_ok=True)
    summaries = {}
    all_rows = {}
    for strategy in ("fixed", "sentence"):
        summary, rows = evaluate_strategy(strategy, docs, eval_set, reranker)
        summaries[strategy] = summary
        all_rows[strategy] = rows
        with open(results_dir / f"per_question_{strategy}.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    with open(results_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2)
    return summaries, all_rows, reranker.available
