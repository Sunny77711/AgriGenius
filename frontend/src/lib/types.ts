export type ChatRequest = {
  query: string;
  language: "auto" | "en" | "hi";
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
  language: "hi" | "en";
  grounded: boolean;
  confidence: "high" | "medium" | "low";
  sources: SourcePassage[];
};

export type HealthResponse = {
  status: string;
  collection_count: number;
  model: string;
};

export type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  responseDetails?: ChatResponse;
};
