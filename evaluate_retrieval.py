"""
Local retrieval evaluation for AgriGenius.

This script does not call Gemini. It checks whether retrieved KCC sources match
the expected crop and broad advisory category for a small, transparent demo set.
"""

import argparse
import json

from rag_pipeline import AgriGeniusRAG


DEFAULT_QUERY_FILE = "demo_queries.json"


def _contains(value, expected):
    return expected.lower() in str(value).lower()


def evaluate(query_file: str, top_k: int, fetch_k: int) -> None:
    with open(query_file, encoding="utf-8") as file:
        cases = json.load(file)

    rag = AgriGeniusRAG()
    crop_hits = 0
    category_hits = 0

    print(f"Collection size: {rag.collection_count():,}")
    print(f"Evaluating {len(cases)} demo queries\n")

    for idx, case in enumerate(cases, 1):
        sources = rag.retrieve_sources(case["query"], top_k=top_k, fetch_k=fetch_k)
        crop_hit = any(_contains(source.metadata.get("Crop", ""), case["expected_crop"]) for source in sources)
        category_hit = any(
            _contains(source.metadata.get("QueryType", ""), case["expected_query_type"]) for source in sources
        )
        crop_hits += int(crop_hit)
        category_hits += int(category_hit)

        top_labels = [
            f"{source.metadata.get('Crop', '?')} / {source.metadata.get('QueryType', '?')}"
            for source in sources
        ]
        print(f"{idx}. {case['query']}")
        print(f"   Expected: {case['expected_crop']} / {case['expected_query_type']}")
        print(f"   Retrieved: {top_labels}")
        print(f"   Crop hit: {'yes' if crop_hit else 'no'} | Category hit: {'yes' if category_hit else 'no'}\n")

    n = len(cases)
    print("=" * 72)
    print(f"Crop hit rate@{top_k}: {crop_hits}/{n} ({crop_hits / n * 100:.1f}%)")
    print(f"Category hit rate@{top_k}: {category_hits}/{n} ({category_hits / n * 100:.1f}%)")
    print("=" * 72)


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate local retrieval on demo queries.")
    parser.add_argument("--query-file", default=DEFAULT_QUERY_FILE)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--fetch-k", type=int, default=20)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    evaluate(args.query_file, args.top_k, args.fetch_k)
