"""Compare configured generators and score claim support with a Gemini judge."""

import argparse
import asyncio
import json
from collections import defaultdict
from pathlib import Path

from rag_pipeline import AgriGeniusRAG


def summarize(results: list[dict]) -> dict:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for result in results:
        language = result.get("language", "Unspecified")
        for model in result.get("comparison", {}).get("models", []):
            grouped[(language, model["provider"])].append(model)

    summary = {}
    for (language, provider), model_results in grouped.items():
        completed = [row for row in model_results if row.get("status") == "ok"]
        scored = [row for row in completed if row.get("metrics")]
        summary.setdefault(language, {})[provider] = {
            "cases": len(model_results),
            "successful_generations": len(completed),
            "scored_cases": len(scored),
            "mean_generation_latency_ms": (
                sum(row["generation_latency_ms"] for row in completed) / len(completed)
                if completed else None
            ),
            "mean_evidence_token_coverage": (
                sum(row["metrics"]["evidence_token_coverage"] for row in scored) / len(scored)
                if scored else None
            ),
            "mean_question_token_coverage": (
                sum(row["metrics"]["question_token_coverage"] for row in scored) / len(scored)
                if scored else None
            ),
            "mean_unmatched_token_share_proxy": (
                sum(row["metrics"]["unmatched_token_share_proxy"] for row in scored) / len(scored)
                if scored else None
            ),
            "mean_semantic_faithfulness_estimate": mean_metric(scored, "semantic_faithfulness"),
            "mean_answer_relevance_estimate": mean_metric(scored, "answer_relevance"),
            "mean_reference_correctness_estimate": mean_metric(scored, "factual_correctness"),
            "mean_unverified_claim_rate_estimate": mean_metric(scored, "unsupported_claim_rate"),
        }
    return summary


def mean_metric(rows: list[dict], metric: str) -> float | None:
    values = [row["metrics"].get(metric) for row in rows]
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else None


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query-file", default="demo_queries.json")
    parser.add_argument("--output", default="llm_evaluation_results.json")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    with open(args.query_file, encoding="utf-8") as file:
        cases = json.load(file)
    if not cases:
        parser.error("The query file must contain at least one case.")

    rag = AgriGeniusRAG()
    results = []
    for index, case in enumerate(cases, start=1):
        query = case.get("query", "").strip()
        if not query:
            print(f"Skipping case {index}: missing query")
            continue
        comparison = await rag.compare_models(
            query,
            top_k=args.top_k,
            reference_answer=case.get("reference_answer"),
        )
        results.append({
            "case_id": case.get("id", index),
            "language": case.get("language", "Unspecified"),
            "expected_crop": case.get("expected_crop"),
            "expected_query_type": case.get("expected_query_type"),
            "reference_answer": case.get("reference_answer"),
            "comparison": comparison,
        })
        statuses = ", ".join(
            f"{model['provider']}={model['status']}"
            for model in comparison["models"]
        )
        print(f"[{index}/{len(cases)}] {case.get('language', 'Unspecified')}: {statuses}; judge={comparison['evaluation']['status']}")

    output = {
        "query_file": str(Path(args.query_file)),
        "model_ids": {"qwen": rag.qwen_model_name, "groq": rag.groq_model_name, "groq_120b": rag.groq_large_model_name},
        "evaluation_method": "gemini_claim_level_judge_v1",
        "judge_model": rag.judge_model_name,
        "results": results,
        "summary_by_language_and_provider": summarize(results),
        "limitations": [
            "This set is exploratory unless its questions and reference answers have been reviewed by agricultural experts.",
            "Semantic faithfulness, relevance, and claim verdicts are Gemini judge estimates and are not ground truth.",
            "Token overlap is sensitive to wording, inflection, spelling, and language; human review is needed, especially for Hindi and Telugu.",
            "Reference-based correctness is scored only when a reviewed reference answer is present; it does not establish objective truth.",
            "Unverified-claim rate is the share of claims judged unsupported or contradicted by retrieved evidence; it is not a definitive hallucination detector.",
        ],
    }
    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)
    print(f"Saved run details and per-language summaries to {args.output}")
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
