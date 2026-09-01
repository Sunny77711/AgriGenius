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
- Implemented a basic RAG pipeline in `kcc_rag_query.py`.
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
- Hindi retrieval is strong for the checked examples.
- English retrieval can hit the correct crop, but can also retrieve weak or question-like passages.
- Near-duplicate flooding is a known issue and should be addressed before final showcase.

## Known Gaps

- No Streamlit or web UI yet.
- No source/citation display in the user-facing answer.
- No duplicate-aware retrieval or MMR diversification yet.
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
