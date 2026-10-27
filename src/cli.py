"""CLI: ingest, ask, evaluate.

    python -m src.cli ingest --strategy sentence
    python -m src.cli ask --strategy sentence "How many days of annual leave?"
    python -m src.cli evaluate
"""

import argparse
import json

from src.chunking import chunk_corpus
from src.config import CORPUS_DIR, EVAL_PATH, INDEX_DIR, RESULTS_DIR
from src.evaluate import run_evaluation
from src.loaders import load_corpus
from src.qa import ask
from src.retrieval import Index, Reranker


def cmd_ingest(args):
    docs = load_corpus(CORPUS_DIR)
    chunks = chunk_corpus(docs, args.strategy)
    index = Index(chunks)
    out = INDEX_DIR / args.strategy
    index.save(out)
    print(f"Indexed {len(chunks)} chunks ({args.strategy}) -> {out}")


def cmd_ask(args):
    index_dir = INDEX_DIR / args.strategy
    if (index_dir / "chunks.json").exists():
        index = Index.load(index_dir)
    else:
        docs = load_corpus(CORPUS_DIR)
        index = Index(chunk_corpus(docs, args.strategy))
    result = ask(args.question, index, Reranker())
    print(f"Answer: {result['answer']}")
    print(f"Source: {result['citation']}")
    for r in result["results"][1:]:
        print(f"  also: {r['citation']}")


def cmd_evaluate(args):
    summaries, _, reranker_ok = run_evaluation(CORPUS_DIR, EVAL_PATH, RESULTS_DIR)
    print(f"Reranker: {'cross-encoder' if reranker_ok else 'hybrid-fallback'}")
    for strategy, s in summaries.items():
        print(
            f"{strategy}: hit@5={s['hit_rate@5']:.3f} "
            f"hit@1={s['hit_rate@1']:.3f} "
            f"accuracy={s['accuracy']:.3f} "
            f"phrase_survival={s['gold_phrase_survival']:.3f} "
            f"({s['n_questions']} questions, {s['n_chunks']} chunks)"
        )
    print(f"Results written to {RESULTS_DIR}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ingest")
    p.add_argument("--strategy", choices=["fixed", "sentence"], default="sentence")
    p.set_defaults(fn=cmd_ingest)
    p = sub.add_parser("ask")
    p.add_argument("question")
    p.add_argument("--strategy", choices=["fixed", "sentence"], default="sentence")
    p.set_defaults(fn=cmd_ask)
    p = sub.add_parser("evaluate")
    p.set_defaults(fn=cmd_evaluate)
    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
