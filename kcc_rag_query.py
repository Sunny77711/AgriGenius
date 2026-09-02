"""Command-line runner for the AgriGenius RAG pipeline."""

import argparse
import sys

from rag_pipeline import AgriGeniusRAG, DEFAULT_FETCH_K, DEFAULT_TOP_K


TEST_QUERIES = [
    "What is the seed rate for groundnut crop?",
    "गेहूं की फसल में सिंचाई कब करनी चाहिए?",
    "How do I control pests in mango trees?",
    "धान की फसल में खरपतवार को कैसे नियंत्रित करें?",
]

def print_query_result(rag, query, top_k, fetch_k, no_llm):
    print("=" * 100)
    print(f"QUERY: {query}")
    print("=" * 100)

    sources = rag.retrieve_sources(query, top_k=top_k, fetch_k=fetch_k)
    print(f"\nRetrieved {len(sources)} diversified source passages:")
    for source in sources:
        print(
            f"  [{source.rank}] sim={source.similarity:.3f} | "
            f"{source.metadata.get('Crop', '?')} | "
            f"{source.metadata.get('QueryType', '?')} | "
            f"{source.text[:120]}"
        )

    if no_llm:
        print("\n[LLM call skipped] Use without --no-llm to generate the final answer.")
        return

    try:
        answer = rag.generate_answer(query, sources)
        print(f"\nANSWER:\n{answer}\n")
    except RuntimeError as e:
        print(f"\n[LLM call skipped] {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Run AgriGenius RAG from the command line.")
    parser.add_argument("--interactive", action="store_true", help="Ask custom questions interactively.")
    parser.add_argument("--no-llm", action="store_true", help="Run retrieval only without calling Gemini.")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help="Number of sources to return.")
    parser.add_argument(
        "--fetch-k",
        type=int,
        default=DEFAULT_FETCH_K,
        help="Number of raw candidates to fetch before filtering/diversification.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print("Loading AgriGenius RAG pipeline ...")
    rag = AgriGeniusRAG()
    print(f"Collection loaded: {rag.collection_count():,} vectors.\n")

    if args.interactive:
        print("Interactive mode. Type a query (English or Hindi), or 'quit' to exit.\n")
        while True:
            query = input("Query> ").strip()
            if query.lower() in ("quit", "exit"):
                break
            if not query:
                continue
            print_query_result(rag, query, args.top_k, args.fetch_k, args.no_llm)
    else:
        for query in TEST_QUERIES:
            print_query_result(rag, query, args.top_k, args.fetch_k, args.no_llm)


if __name__ == "__main__":
    main()
