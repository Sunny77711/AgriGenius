# AgriGenius

AgriGenius is an English-Hindi farming assistant that uses Retrieval-Augmented Generation (RAG) to answer farmer queries with evidence from real Kisan Call Centre (KCC) advisory records. The project focuses on practical agricultural questions such as irrigation, pest control, sowing, fertilizer use, weed management, crop care, and government-scheme guidance.

The current prototype includes a cleaned KCC retrieval corpus, a ChromaDB vector index, and a Gemini-based answer generation pipeline. The product is being extended into a full farmer-facing assistant with a polished UI, source-backed answers, duplicate-aware retrieval, evaluation reports, and optional voice interaction.

## Current Status

Implemented:

- KCC raw data pooling and exploratory analysis.
- Cleaning pipeline for whitespace issues, missing fields, short answers, corrupted sector rows, duplicate answers, stale weather-heavy content, and PII-sensitive entries.
- Final retrieval corpus with 347,944 cleaned advisory records.
- ChromaDB vector index with 347,944 vectors.
- Hindi-aware embedding model: `l3cube-pune/hindi-sentence-bert-nli`.
- Reusable RAG pipeline: ChromaDB retrieval -> source selection -> grounded Gemini generation.
- Source-returning retrieval output for future UI citation cards.
- Automatic crop/query-type metadata filtering for clear farmer queries.
- Duplicate-aware candidate filtering with MMR-style diversification.
- Local retrieval diagnostics for cross-lingual retrieval, non-answer rows, and near-duplicate flooding.

Planned / in progress:

- Streamlit-based farmer UI.
- Streamlit display of retrieved source/citation cards.
- Reranking and improved English-Hindi retrieval fusion.
- Evaluation against non-RAG baselines and held-out agricultural QA benchmarks.
- Voice input/output for low-literacy accessibility.

## Repository Structure

```text
.
├── clean_filter.py
├── data_quality_recheck.py
├── eda_analysis.py
├── embedding.py
├── first_analysis.py
├── kcc_build_index.py
├── kcc_rag_query.py
├── kcc_strip_pii.py
├── qualitative_retrieval_check.py
├── rag_pipeline.py
├── evaluate_retrieval.py
├── demo_queries.json
├── retrieval_diagnostics.py
├── sowing_time_weather_spotcheck.py
├── weather_cleanup.py
├── weather_cleanup_check.py
├── docs/
│   ├── project_status.md
│   ├── pipeline.md
│   └── github_contribution_plan.md
├── requirements.txt
└── .env.example
```

Large datasets, the local ChromaDB index, virtual environments, checkpoints, and API keys are intentionally excluded from Git.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your Gemini API key:

```bash
cp .env.example .env
```

Edit `.env` and add your own key:

```bash
GEMINI_API_KEY=your_key_here
```

Then export it before running the RAG script:

```bash
export GEMINI_API_KEY="your_key_here"
```

## Running The Current Prototype

The current RAG prototype expects a local ChromaDB index at:

```text
./chroma_kcc_db
```

Run the built-in test queries:

```bash
python kcc_rag_query.py
```

Run retrieval only without calling Gemini:

```bash
python kcc_rag_query.py --no-llm
```

Run interactive mode:

```bash
python kcc_rag_query.py --interactive
```

Run local retrieval evaluation:

```bash
python evaluate_retrieval.py --top-k 5 --fetch-k 50
```

## Dataset Note

The full KCC CSV files and ChromaDB index are not committed because they are large local artifacts. See `docs/pipeline.md` for the processing flow and expected local files.

## Team

- K V Ravi Teja - Frontend and conversational interface
- V Mokshagnna Bramha Teja - RAG backend and Gemini integration
- T Rushil Chakravarthy - Data pipeline and vector index construction
- Tejasvi Senka - Evaluation, diagnostics, and safety checks
