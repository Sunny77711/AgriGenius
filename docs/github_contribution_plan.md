# GitHub Contribution Plan

This plan maps commits and future branches to the contribution roles shown in the project presentation.

## Commit Strategy

Use small commits grouped by project layer. Each team member should commit the files that match their contribution area. This keeps the history honest and makes the final presentation easier to justify.

## Recommended Initial Commits

### 1. Repository Setup

Suggested owner: any team member

Files:

- `.gitignore`
- `README.md`
- `requirements.txt`
- `.env.example`
- `docs/project_status.md`
- `docs/pipeline.md`
- `docs/github_contribution_plan.md`

Commit message:

```bash
git commit -m "Set up AgriGenius project repository"
```

### 2. Data Pipeline

Suggested owner: T Rushil Chakravarthy

Files:

- `clean_filter.py`
- `kcc_strip_pii.py`
- `sowing_time_weather_spotcheck.py`
- `weather_cleanup.py`
- `weather_cleanup_check.py`
- `kcc_build_index.py`

Commit message:

```bash
git commit -m "Add KCC cleaning and indexing pipeline"
```

### 3. RAG Backend

Suggested owner: V Mokshagnna Bramha Teja

Files:

- `kcc_rag_query.py`
- `embedding.py`
- `qualitative_retrieval_check.py`

Commit message:

```bash
git commit -m "Add ChromaDB retrieval and Gemini RAG pipeline"
```

### 4. Evaluation And Safety

Suggested owner: Tejasvi Senka

Files:

- `retrieval_diagnostics.py`
- `data_quality_recheck.py`
- `eda_analysis.py`
- `first_analysis.py`

Commit message:

```bash
git commit -m "Add retrieval diagnostics and data quality checks"
```

## Branch Plan For Next Development

### Frontend Branch

Owner: K V Ravi Teja

```bash
git checkout -b feature/streamlit-ui
```

Tasks:

- Build Streamlit UI.
- Add Hindi/English query box.
- Add optional crop and district fields.
- Add answer display.
- Add retrieved source cards.

### Backend Retrieval Branch

Owner: V Mokshagnna Bramha Teja

```bash
git checkout -b feature/rag-backend-upgrades
```

Tasks:

- Refactor RAG logic into reusable functions.
- Add source/citation output.
- Add stronger prompt template.
- Add confidence or insufficient-evidence handling.

### Data Quality Branch

Owner: T Rushil Chakravarthy

```bash
git checkout -b feature/data-quality
```

Tasks:

- Improve non-answer filtering.
- Add duplicate-aware retrieval support.
- Document local dataset reconstruction steps.

### Evaluation Branch

Owner: Tejasvi Senka

```bash
git checkout -b feature/evaluation
```

Tasks:

- Add fixed demo query set.
- Add retrieval hit-rate evaluation.
- Add RAG vs non-RAG comparison.
- Prepare result table for final PPT.

## Before Every Commit

Run:

```bash
git status --short
```

Never commit:

- `keys.env`
- `.env`
- `.venv/`
- `__pycache__/`
- `chroma_kcc_db/`
- Full KCC CSV files
- `kcc_index_checkpoint.json`

## First Push

After the initial commits:

```bash
git branch -M main
git push -u origin main
```
