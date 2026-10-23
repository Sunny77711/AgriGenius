# AgriGenius

AgriGenius is a local RAG prototype for agricultural questions in Hindi, Telugu, and English. It retrieves evidence from Kisan Call Centre (KCC) advisories and passes selected passages to a grounded answer generator.

## Current Local Artifacts

- Retrieval corpus: `kcc_index_ready_final.csv` — **493,213 rows**.
- ChromaDB collection: `chroma_kcc_db/kcc_agri_advisor` — **493,213 vectors**.
- Embeddings: `l3cube-pune/indic-sentence-bert-nli`, 768 dimensions, normalized, cosine distance.
- Reranker: `BAAI/bge-reranker-v2-m3` (configured; requires model access on first load).
- Answer providers: Groq-hosted Qwen `qwen/qwen3.8-27b` and Groq `openai/gpt-oss-20b`.
- UI/API: React + Vite frontend and FastAPI backend, with SSE chat streaming.

The local Chroma collection records the embedding model, dimensions, normalization, metric, source row count, and SHA-256 fingerprint of the indexed corpus. The Kaggle build notebook `nlp-run1.ipynb` records a 493,213-row build using the same Indic model and normalized 768-dimensional vectors. The separate engineering summary's 508,072 cleaned-row figure does not match the current local corpus and should not be used as the active count.

## Readiness

The current state is a development prototype. Live multilingual retrieval, three-generator comparison, Gemini claim-level judging, and the BGE reranker still need end-to-end evaluation before a public or farmer-facing deployment. The application fails visibly when the backend is unavailable; it does not substitute sample agricultural answers.

## Setup

Create and activate a virtual environment, then install the Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set `GROQ_API_KEY` for the Qwen and GPT-OSS generators and `GEMINI_API_KEY` for the claim-level evaluation judge. Optional model overrides are `AGRI_QWEN_MODEL`, `AGRI_GROQ_MODEL`, `AGRI_GROQ_LARGE_MODEL`, and `AGRI_EVAL_JUDGE_MODEL`. Both `.env` and `keys.env` are ignored by Git.

Chat uses Qwen as its primary generator and retries with GPT-OSS if Qwen fails before returning an answer. The assistant identifies the model used. Both generators use Groq, so this fallback can recover from a model-specific error but not from a Groq outage or missing API key.

Run the API from the repository root:

```bash
uvicorn backend.server:app --host 127.0.0.1 --port 8000
```

Run the farmer-facing public frontend in a second terminal (Port 5173):

```bash
cd frontend
npm install
npm run dev
```

Run the standalone National Admin Command Center in a third terminal (Port 5174):

```bash
cd admin
npm install
npm run dev
```

- Public Farmer Site: `http://localhost:5173`
- Dedicated Admin Command Center: `http://localhost:5174`
- FastAPI Documentation & Endpoints: `http://localhost:8000/docs`

## Build and Evaluation

Build or rebuild the Chroma index from the current local corpus with the same embedding model used by the RAG query path:

```bash
python kcc_build_index.py
```

The builder refuses to mix a different embedding model into an existing collection. It uses the corpus fingerprint and model ID when resuming batch checkpoints.

Run local retrieval evaluation:

```bash
python evaluate_retrieval.py --top-k 5 --fetch-k 20
```

Check live generation abstention with the configured provider credentials:

```bash
python evaluate_abstention.py --provider qwen
```

The retrieval check uses a small demo set only; it is not a held-out agricultural QA benchmark. Run both checks with model access before deployment.

The UI's **LLM QA** page compares Qwen 3.8 27B, GPT-OSS 20B, and GPT-OSS 120B on shared retrieved KCC passages. One Gemini 3.5 Flash-Lite judge call then returns claim-level source-support verdicts, semantic faithfulness and relevance estimates, and explanations. Reference-based correctness is available only when a reviewed reference answer is provided. The judge is not a factual oracle; see [docs/llm_evaluation_report.md](docs/llm_evaluation_report.md) for the protocol and limitations. The source drawer's LIME explanation describes the BGE reranker score, which is a separate XAI target.

Run a batch comparison over the multilingual smoke set and save per-case output plus language/provider averages:

```bash
python evaluate_llms.py --query-file demo_queries.json --output llm_evaluation_results.json
```

For formal evaluation, use a larger reviewed file with multiple cases per language and reference answers. Treat the checked-in demo set as exploratory only.

## Data and Index Files

Raw KCC files, processed CSVs, ChromaDB stores, model checkpoints, virtual environments, and credentials are local artifacts and are not committed. See [docs/pipeline.md](docs/pipeline.md) and [docs/project_status.md](docs/project_status.md) for the verified local pipeline state and remaining readiness checks.
