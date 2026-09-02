# AgriGenius Project Status

Last updated: 2026-09-01

## One-Line Summary

AgriGenius is currently a working local RAG backend prototype over cleaned Kisan Call Centre data. It is not yet a fully polished product because the UI, source display, evaluation report, and retrieval improvements still need to be built.

## What Is Done

- Pooled raw KCC data for the working corpus.
- Completed exploratory analysis of missing fields, query types, script distribution, and answer lengths.
- Cleaned KCC data by removing short answers, corrupted sector rows, exact duplicates, weather query rows, stale scheme rows, PII-sensitive rows, and weather-heavy sowing rows.
- Created `kcc_index_ready_final.csv` locally with 347,944 cleaned advisory records.
- Built a persistent ChromaDB collection named `kcc_agri_advisor`.
- Confirmed the ChromaDB collection contains 347,944 vectors.
- Selected `l3cube-pune/hindi-sentence-bert-nli` as the embedding model.
- Implemented a reusable RAG pipeline in `rag_pipeline.py`.
- Updated `kcc_rag_query.py` into a CLI wrapper around the reusable pipeline.
- Added source-returning retrieval outputs for future UI citation/source cards.
- Added automatic crop/query-type metadata filtering for explicit farmer queries.
- Added duplicate-aware candidate filtering with MMR-style diversification.
- Added `evaluate_retrieval.py` and `demo_queries.json` for local retrieval evaluation.
- Implemented diagnostics for cross-lingual retrieval, non-answer rows, and near-duplicate flooding.

## Current Verification Results

- Python scripts compile successfully.
- Core imports work in the local virtual environment:
  - `pandas`
  - `chromadb`
  - `sentence-transformers`
  - `google-genai`
- Local ChromaDB collection loads successfully.
- Local retrieval works for Hindi and English queries.
- Retrieval-only CLI smoke test works with `python kcc_rag_query.py --no-llm --top-k 5 --fetch-k 50`.
- Demo retrieval evaluation works with `python evaluate_retrieval.py --top-k 5 --fetch-k 50`.
- Current demo evaluation result: crop hit rate@5 = 6/6, category hit rate@5 = 6/6.
- Near-duplicate flooding is improved through candidate filtering and MMR-style diversification, but should still be monitored.

## Known Gaps

- No Streamlit or web UI yet.
- No finished Streamlit source/citation display yet.
- No reranking layer yet.
- No full RAG vs non-RAG evaluation yet.
- No held-out AgriSci-QA evaluation yet.
- No voice input/output yet.
- No deployment packaging yet.

## Recommended Product Maturity Label

Current Technology Readiness Level: TRL 4

Justification:

- The core technical components work in a local development environment.
- Data cleaning, indexing, retrieval, and generation have been validated locally.
- The product has not yet been validated as a polished user-facing system in a realistic usage environment.

Target for final showcase: TRL 5

To reach TRL 5:

- Add a working UI.
- Add visible retrieved sources.
- Add duplicate-aware retrieval.
- Add a fixed demo query set.
- Add evaluation results.
- Record a clean end-to-end demo.
