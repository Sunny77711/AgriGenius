# AgriGenius Product Pipeline

## Overall Product Flow

```text
Farmer query
  -> Language/input handling
  -> Query embedding
  -> ChromaDB retrieval from cleaned KCC corpus
  -> Candidate filtering and duplicate reduction
  -> Grounded prompt construction
  -> Gemini LLM answer generation
  -> Same-language farmer response
  -> Source display and uncertainty message
  -> Evaluation and feedback logging
```

## Offline Data Pipeline

```text
Raw KCC CSV files
  -> Pool state/year files
  -> Clean whitespace and malformed values
  -> Drop unusable columns such as Season
  -> Remove short or empty KccAns values
  -> Remove corrupted Sector rows
  -> Exclude Weather query type
  -> Apply recency cutoff for Government Schemes
  -> Collapse exact duplicate KccAns values
  -> Strip PII-sensitive rows
  -> Remove weather-heavy Sowing Time and Weather rows
  -> Save final corpus
  -> Embed KccAns values
  -> Store vectors and metadata in ChromaDB
```

Local output files:

- `kcc_pooled.csv`
- `kcc_index_ready.csv`
- `kcc_index_ready_final.csv`
- `chroma_kcc_db/`

These files are intentionally ignored by Git because they are large local artifacts.

## Online RAG Pipeline

```text
User asks a question in Hindi or English
  -> Encode query with l3cube-pune/hindi-sentence-bert-nli
  -> Retrieve top-k advisory records from ChromaDB
  -> Build context block with KCC answer text and metadata
  -> Send grounded prompt to Gemini
  -> Generate concise practical response
  -> Return answer in the same language as the user query
```

## LLM Module Design

### Technology View

- Embedding model: `l3cube-pune/hindi-sentence-bert-nli`
- Vector database: ChromaDB
- Generation model: Gemini through `google-genai`
- Retrieval count: top-k retrieval, currently `TOP_K = 5`
- Prompt inputs:
  - Farmer query
  - Retrieved KCC answer passages
  - Crop metadata
  - District metadata
  - Query type metadata
- System instruction:
  - Answer only from retrieved context
  - Keep response practical and concise
  - Use the same language as the farmer query
  - Say when evidence is insufficient

### Functional View

The LLM module is designed to act as a grounded agricultural advisor rather than a free-form chatbot. It does not directly answer from memory. Instead, it receives retrieved expert advisory passages and converts them into a clear farmer-facing response.

Expected behavior:

- Provide crop-specific, practical guidance.
- Avoid unsupported recommendations.
- Preserve Hindi or English based on the user's query.
- Keep the answer short enough for real farmer use.
- Add uncertainty handling when retrieval evidence is weak.

## Planned Product Enhancements

- Streamlit UI for farmer interaction.
- Visible source cards showing retrieved KCC passages.
- MMR or duplicate-aware candidate filtering.
- Optional metadata filters for crop, region, and query type.
- English-Hindi retrieval fusion for stronger cross-lingual retrieval.
- Cross-encoder reranking.
- RAG vs non-RAG evaluation.
- Held-out AgriSci-QA evaluation.
- Voice input and voice output.
