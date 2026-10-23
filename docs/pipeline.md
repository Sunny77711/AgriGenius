# AgriGenius Product Pipeline

## Offline Corpus and Index

The current local artifacts form this verified path:

```text
KCC source exports
  -> pooled and cleaned source files
  -> kcc_index_ready_final.csv (493,213 rows)
  -> l3cube-pune/indic-sentence-bert-nli
  -> normalized 768-dimensional embeddings
  -> ChromaDB cosine collection: kcc_agri_advisor (493,213 vectors)
```

The Kaggle build procedure is recorded in `nlp-run1.ipynb`. Its output records 493,213 input rows and 1,927 completed batches using the Indic sentence model. The local index agrees with that count and model. The index builder records the model ID, output dimension, normalization, metric, source row count, and a SHA-256 fingerprint; its resume checkpoint also checks model and corpus fingerprint before skipping batches.

The index collection contains advisory text and crop, district, state, query type, sector, and date metadata. The final CSV's `language` column is empty, so script presence in text must not be represented as a complete language annotation.

## Online RAG Path

```text
Hindi / Telugu / English farmer question
  -> Indic sentence embedding
  -> cosine retrieval from ChromaDB (fetch-k candidates)
  -> remove likely question-only rows and near duplicates
  -> BAAI/bge-reranker-v2-m3 cross-encoder reranking
  -> top-k KCC passages and metadata
  -> Groq Qwen 3.8 27B or Groq openai/gpt-oss-20b generation
  -> SSE answer chunks with source metadata
```

The prompt requires answers to stay within the retrieved KCC context, cite source ranks, use the query language when possible, and abstain when evidence is insufficient. Chat uses Qwen as the primary generator and retries once with GPT-OSS if the primary call fails before returning an answer. The response identifies the model that produced it. If both fail, the API surfaces an error instead of returning invented text. In streaming mode, fallback is possible only before the first answer chunk; an error after partial output is surfaced.

## API and Frontend

- `GET /api/health` reports the live collection size and configured embedding, reranker, and generation models.
- `POST /api/chat` returns a complete answer and source list.
- `POST /api/chat/stream` sends source metadata and answer chunks as SSE.
- `POST /api/llm/compare` retrieves once, runs three configured generators concurrently on identical evidence, then makes one Gemini call to judge claim support and answer relevance. Optional reviewed reference text enables a reference-alignment estimate.
- `POST /api/explain` applies LIME text perturbations to explain one BGE reranker score for the requested ranked passage.
- The `/evaluation` UI shows three generator outputs, timings, semantic judge estimates, claim verdicts with source ranks/rationales, and secondary lexical diagnostics.
- The normal chat assistant uses Qwen via Groq with GPT-OSS via Groq as its fallback; the chat answer shows which model responded.
- `python evaluate_llms.py --query-file demo_queries.json` runs the same dual-model comparison over the query file and writes per-case results plus per-language/provider summaries to `llm_evaluation_results.json`.
- Vite proxies `/api` to `http://127.0.0.1:8000` during development.
- When the backend is unavailable, the frontend reports that state and shows an error on chat requests. It does not show hard-coded sample answers or citations as grounded output.
- Set `AGRI_CORS_ORIGINS` for deployment origins. The local defaults allow the Vite development origin.

## Validation Status

Local record counts, sampled corpus/index alignment, Chroma cosine configuration, provenance metadata, and the frontend production build have been checked. Retrieval quality across languages, abstention under live generation, provider behavior, and deployment remain pending an online end-to-end validation run. The small demo query set is a smoke check, not a benchmark.

Install `lime` for source-card explanations, `groq` for the three Groq generators, and `google-genai` for semantic judging. Qwen (`AGRI_QWEN_MODEL`, default `qwen/qwen3.8-27b`), GPT-OSS 20B (`AGRI_GROQ_MODEL`, default `openai/gpt-oss-20b`), and GPT-OSS 120B (`AGRI_GROQ_LARGE_MODEL`, default `openai/gpt-oss-120b`) use `GROQ_API_KEY`. The single custom Gemini judge (`AGRI_EVAL_JUDGE_MODEL`, default `gemini-3.5-flash-lite`) uses `GEMINI_API_KEY`; it is bounded to 35 seconds at the HTTP layer and 40 seconds by the evaluation coroutine. If judging fails, the answer outputs and lexical diagnostics remain visible while semantic scores are pending. Judge outputs are estimates, not ground truth; reference-based correctness is not scored without reviewed reference text.

Run `python evaluate_retrieval.py --top-k 5 --fetch-k 20` for per-language crop/category hit rates and `python evaluate_abstention.py --provider qwen` for the unsupported Mars cultivation prompt. These require the embedding and reranker models; the abstention check also requires provider credentials.
