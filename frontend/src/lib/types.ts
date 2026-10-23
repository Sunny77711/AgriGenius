export type ChatRequest = {
  query: string;
  language: "auto" | "en" | "hi" | "te";
  crop?: string;
  district?: string;
  top_k?: number;
};

export type SourceMetadata = {
  Crop?: string;
  DistrictName?: string;
  QueryType?: string;
  StateName?: string;
  source?: string;
};

export type SourcePassage = {
  rank: number;
  text: string;
  similarity: number;
  metadata: SourceMetadata;
};

export type ChatResponse = {
  answer: string;
  query?: string;
  language: "hi" | "te" | "en";
  grounded: boolean;
  confidence: "high" | "medium" | "low" | "unknown";
  sources: SourcePassage[];
  generation?: {
    provider: "qwen" | "groq" | null;
    model: string | null;
    fallback_used: boolean;
    fallback_reason?: string | null;
  };
};

export type GenerationInfo = NonNullable<ChatResponse["generation"]>;

export type ModelComparisonResult = {
  provider: 'qwen' | 'groq' | 'groq_120b';
  model: string;
  status: 'ok' | 'error';
  answer: string | null;
  generation_latency_ms: number;
  answer_characters?: number;
  error?: string;
  claim_reviews?: Array<{
    claim: string;
    verdict: 'supported' | 'contradicted' | 'not_found';
    source_ranks: number[];
    rationale: string;
  }>;
  metrics?: {
    evidence_token_coverage: number;
    question_token_coverage: number;
    unmatched_token_share_proxy: number;
    semantic_faithfulness: number | null;
    answer_relevance: number | null;
    factual_correctness: number | null;
    unsupported_claim_rate: number | null;
    contradicted_claim_rate: number | null;
  };
};

export type ModelComparison = {
  query: string;
  models: ModelComparisonResult[];
  sources: SourcePassage[];
  source_count: number;
  reference_answer_provided: boolean;
  evaluation: {
    method: string;
    judge_model: string;
    status: string;
    judge_latency_ms: number | null;
    error: string | null;
    note: string;
  };
};

export type LimeExplanation = {
  status: string;
  method?: string;
  target?: string;
  source_rank?: number;
  reranker_score?: number;
  num_samples?: number;
  feature_weights?: Array<{ token: string; weight: number }>;
  note?: string;
  reason?: string;
};

export type HealthResponse = {
  status: string;
  collection_count?: number;
  model?: string;
  reranker?: string;
  llm_model?: string;
  llm_models?: { qwen?: string; groq?: string; groq_120b?: string };
  evaluation_method?: string;
  evaluation_judge?: string;
};

export type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  responseDetails?: ChatResponse;
};
