# LLM Evaluation Protocol and Current Status

## Models and request flow

The `/evaluation` page retrieves Kisan Call Centre passages once, then runs three generators concurrently against that same question and evidence:

| Generator | Provider | Default model ID |
|---|---|---|
| Qwen 3.8 27B | Groq | `qwen/qwen3.8-27b` |
| GPT-OSS 20B | Groq | `openai/gpt-oss-20b` |
| GPT-OSS 120B | Groq | `openai/gpt-oss-120b` |

After generation, one Gemini 3.5 Flash-Lite request reviews all successful answers together. This is a custom claim-level evaluator; RAGAS is not used. The scorer is configurable with `AGRI_EVAL_JUDGE_MODEL` and requires `GEMINI_API_KEY`. A failed or timed-out judge leaves semantic fields pending while preserving model answers and local token-overlap diagnostics.

## Judge measures

The judge is instructed to split material factual statements into claims and label each `supported`, `contradicted`, or `not_found` against the supplied retrieved passages. Each review includes a short rationale and source ranks. API score values are between zero and one.

| Measure | Calculation / basis | Interpretation |
|---|---|---|
| Semantic faithfulness estimate | Supported claims divided by all reviewed claims. | Gemini's estimate of what fraction of claims are entailed by retrieved evidence. It can be wrong and is not a proof of truth. |
| Answer relevance estimate | Gemini assigns a 0–1 score for how well the answer addresses the question. | A model-judge estimate, not a human relevance rating or correctness score. |
| Unverified claim rate | Claims labeled `not_found` or `contradicted`, divided by all reviewed claims. | Source-grounding warning. It is not a definitive hallucination detector. |
| Contradicted claim rate | Claims labeled `contradicted`, divided by all reviewed claims. | Highlights conflict with retrieved evidence; the judge may miss contradictions. |
| Reference-based correctness estimate | Gemini compares the answer with an optional reviewed reference answer. | Available only when such a reference is supplied. It measures judged alignment with that reference, not objective truth. |

The optional reference-answer field is intended for reviewed evaluation cases. For the batch runner, provide `reference_answer` in each query JSON record. Live cases without one report reference-based correctness as not scored.

## Local diagnostics and explainability

Evidence-token and question-token coverage remain as secondary lexical diagnostics. They use deterministic Unicode token overlap and should not be called faithfulness or relevance. The claim-level rationale and cited source ranks explain the judge's recorded decision; they do not explain the generators' internal reasoning. The existing LIME integration explains how question tokens affect the BGE reranker's relevance score for a selected source. These are separate explanation targets.

## Limitations and safety

The judge is another model and can miss unsupported details, mishandle negation or quantities, and show language or model bias. “Not found” means the supplied retrieved passages did not establish a claim; it does not necessarily mean the claim is false. The reference-based correctness figure is itself judge-estimated. Use expert-reviewed references and qualified agricultural review for safety-sensitive advice. Do not treat these automated metrics as deployment certification.

## Batch evaluation

```bash
python evaluate_llms.py --query-file <reviewed-cases.json> --output llm_evaluation_results.json
```

Each case stores model IDs, generated answers, retrieved evidence, generation timings, local diagnostics, judge verdicts, and claim rationales. The summary groups generation and score averages by language and provider. Record the run date, model IDs, reviewed case set, judge status, provider errors, and human-review outcomes before citing scores.

## Current results status

| Language / check | Generators | Judge metrics | Status |
|---|---|---|---|
| Hindi | Qwen 3.8 27B, GPT-OSS 20B, GPT-OSS 120B | Claim support, relevance; correctness only with reviewed references | Pending reviewed batch run |
| Telugu | Qwen 3.8 27B, GPT-OSS 20B, GPT-OSS 120B | Claim support, relevance; correctness only with reviewed references | Pending reviewed batch run |
| English | Qwen 3.8 27B, GPT-OSS 20B, GPT-OSS 120B | Claim support, relevance; correctness only with reviewed references | Pending reviewed batch run |

No aggregate model-quality result is claimed until a reviewed multilingual run is completed and inspected. This report does not certify farmer-facing readiness.
