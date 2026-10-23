# AgriGenius Project Status

Last updated: 2026-10-23

## Current State

AgriGenius is a local multilingual RAG development prototype. The checked-in backend and frontend are wired together, and the persistent local index has verified corpus and embedding provenance. This is not a production or TRL 6 sign-off: live retrieval, reranking, generation, safety, and deployment checks remain to be run with online model access.

## Verified Local Artifacts

- `kcc_index_ready_final.csv`: 493,213 rows across Uttar Pradesh (347,928), Maharashtra (106,166), and Andhra Pradesh (39,119).
- Chroma collection `kcc_agri_advisor`: 493,213 vectors.
- Kaggle notebook `nlp-run1.ipynb`: its build output reports loading 493,213 rows and completing 1,927 batches with `l3cube-pune/indic-sentence-bert-nli`.
- Notebook settings and local Chroma configuration agree on normalized 768-dimensional embeddings and cosine distance.
- Local collection metadata now records the embedding model, dimensions, normalization, distance metric, row count, and corpus fingerprint. First, middle, and last indexed records match the current CSV.
- The corpus text contains Devanagari characters in 452,838 rows and Telugu characters in 28,296 rows. These are script-presence counts, not a language-label audit; the CSV `language` field is blank.
- Frontend uses the FastAPI API. Backend failures now surface as errors rather than mock answers. The status panel reports when the API is unavailable.

## Architecture Configuration

- Embedding model: `l3cube-pune/indic-sentence-bert-nli`.
- Vector store: ChromaDB, collection `kcc_agri_advisor`, cosine distance.
- Reranker: `BAAI/bge-reranker-v2-m3`.
- Generation: Groq-hosted Qwen (`qwen/qwen3.8-27b` by default) and Groq GPT-OSS (`openai/gpt-oss-20b`); both can be run against the same evidence through the LLM QA page.
- Evaluation: three concurrent Groq generators followed by one custom Gemini claim-level judge call; no RAGAS dependency. Semantic scores and per-claim source rationales are judge estimates.
- Chat generation: Qwen via Groq is primary; GPT-OSS 20B via Groq is retried once on a pre-answer failure, and the selected model is reported with the response. GPT-OSS 120B is included in the comparison/evaluation page.
- Explainability: on-demand LIME perturbation explanation for the BGE cross-encoder relevance score of a selected source.
- Service: FastAPI with `/api/health`, `/api/chat`, `/api/chat/stream`, `/api/llm/compare`, and `/api/explain`.
- UI: React 19, TypeScript, Vite, with SSE streaming, source cards, a three-generator LLM QA view, Gemini judge estimates, claim-level evidence explanations, and LIME source explanations.

## Readiness Checks Still Required

- Load the Indic embedding model and BGE reranker from Hugging Face in an online environment; confirm startup and index metadata checks.
- Run the updated multilingual retrieval and dual-model comparison checks with Groq access, then record the returned lexical overlap scores and generation failures.
- Run retrieval evaluations for Hindi, Telugu, and English against a reviewed expected-answer set. The current small demo evaluation is not a held-out benchmark.
- Run `evaluate_abstention.py` and chat/streaming requests against Qwen and Groq GPT-OSS; check citations, same-language replies, abstention with insufficient evidence, and provider failures.
- Run dual-model comparisons on a reviewed, multi-case Hindi/Telugu/English evaluation set; record token-overlap indicators and manually review outputs against evidence. These lexical indicators are not semantic quality metrics. The current UI is a per-question live comparison, not an aggregate benchmark.
- Confirm LIME explanations load in the intended environment and review whether the query-token attributions are interpretable for each script.
- Verify deployment-specific `VITE_API_BASE_URL`, `AGRI_CORS_ORIGINS`, secrets, startup, health check, and SSE behavior.
- Complete a broader privacy and agronomic safety review before public farmer use.

## Count Reconciliation

The authoritative local working count is **493,213**, because the current final CSV, local Chroma collection, sampled indexed records, and the index-build notebook agree. The previous repository docs' 347,944 count and the separate engineering summary's 508,072 cleaned-corpus count describe earlier or different artifacts and are not the active local count.

Earlier checks on 2026-10-22 could not complete multilingual retrieval because Hugging Face DNS was unavailable. A Gemini-generation smoke run later failed during RAGAS initialization because Instructor 1.3.2 did not expose `from_genai`; a hosted Llama attempt also hit exhausted Hugging Face credits. The current judge uses the direct Google GenAI SDK without RAGAS or Instructor. Multilingual results still need to be collected and reviewed.

## Model QA and Explainability

The LLM QA screen runs Qwen 3.8 27B, GPT-OSS 20B, and GPT-OSS 120B against the same retrieved passages, then asks Gemini 3.5 Flash-Lite to evaluate all successful answers in one call. Claim verdicts and semantic-faithfulness/relevance scores are estimates. Reference-based correctness is only shown when a reviewed reference answer is supplied; no automated value proves agronomic safety. Source-card LIME explains the BGE reranker score. A credentialed multilingual run and human review remain outstanding.
