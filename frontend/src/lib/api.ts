import type { ChatRequest, ChatResponse, HealthResponse, LimeExplanation, ModelComparison, SourcePassage } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

function isHindi(query: string): boolean {
  return /[\u0900-\u097f]/.test(query);
}

function answerLanguage(query: string, requested: ChatRequest['language']): ChatResponse['language'] {
  if (requested === 'te' || /[\u0c00-\u0c7f]/.test(query)) return 'te';
  if (requested === 'hi' || isHindi(query)) return 'hi';
  return 'en';
}

async function responseError(response: Response): Promise<Error> {
  const detail = await response.text().catch(() => '');
  return new Error(detail || `Backend returned HTTP ${response.status}`);
}

export async function checkHealth(): Promise<HealthResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2000);
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, { signal: controller.signal });
    if (!response.ok) return { status: 'unavailable' };
    return await response.json() as HealthResponse;
  } catch {
    return { status: 'unavailable' };
  } finally {
    clearTimeout(timeout);
  }
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw await responseError(response);

  const result = await response.json() as {
    answer: string;
    sources?: SourcePassage[];
    generation?: ChatResponse["generation"];
  };
  const sources = result.sources || [];
  return {
    answer: result.answer,
    language: answerLanguage(request.query, request.language),
    grounded: sources.length > 0,
    confidence: 'unknown',
    sources,
    generation: result.generation,
  };
}

export async function compareModels(query: string, referenceAnswer?: string): Promise<ModelComparison> {
  const response = await fetch(`${API_BASE_URL}/api/llm/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: 5, reference_answer: referenceAnswer?.trim() || undefined }),
  });
  if (!response.ok) throw await responseError(response);
  return await response.json() as ModelComparison;
}

export async function explainSource(query: string, sourceRank: number): Promise<LimeExplanation> {
  const response = await fetch(`${API_BASE_URL}/api/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, source_rank: sourceRank }),
  });
  if (!response.ok) throw await responseError(response);
  return await response.json() as LimeExplanation;
}

export async function streamChatMessage(
  request: ChatRequest,
  onChunk: (chunk: string) => void,
  onSources: (sources: SourcePassage[]) => void,
  onModel: (generation: NonNullable<ChatResponse['generation']>) => void,
  onError: (error: Error) => void,
  onComplete: () => void
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw await responseError(response);
    if (!response.body) throw new Error('Backend did not return a response stream.');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      const parts = buffer.split(/\r?\n\r?\n/);
      buffer = parts.pop() || '';

      for (const part of parts) {
        for (const line of part.split(/\r?\n/)) {
          if (!line.startsWith('data: ')) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'metadata') onSources(data.sources || []);
            if (data.type === 'model') onModel(data);
            if (data.type === 'chunk') onChunk(data.content || '');
            if (data.type === 'error') throw new Error(data.message || 'Streaming request failed.');
          } catch (error) {
            if (error instanceof SyntaxError) {
              throw new Error('Backend returned invalid streaming data.');
            }
            throw error;
          }
        }
      }

      if (done) break;
    }
    onComplete();
  } catch (error) {
    onError(error instanceof Error ? error : new Error('Unable to reach the AgriGenius backend.'));
  }
}

// ---------------------------------------------------------------------------
// Reports API (Neon PostgreSQL / Database)
// ---------------------------------------------------------------------------

export async function saveReportApi(payload: {
  user_email?: string;
  user_id?: string;
  report_code?: string;
  title: string;
  farmer_name?: string;
  location?: string;
  land_acres?: number;
  soil_type?: string;
  water_availability?: string;
  previous_crop?: string;
  previous_yield?: string;
  next_season?: string;
  budget?: number;
  main_objective?: string;
  top_crop?: string;
  language?: string;
  report_data?: any;
}) {
  const response = await fetch(`${API_BASE_URL}/api/reports`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw await responseError(response);
  return await response.json();
}

export async function fetchReportsApi(userEmail?: string, userId?: string) {
  const params = new URLSearchParams();
  if (userEmail) params.set('user_email', userEmail);
  if (userId) params.set('user_id', userId);
  const response = await fetch(`${API_BASE_URL}/api/reports?${params.toString()}`);
  if (!response.ok) throw await responseError(response);
  return await response.json();
}

export async function deleteReportApi(reportId: number | string, userEmail?: string, userId?: string) {
  const params = new URLSearchParams();
  if (userEmail) params.set('user_email', userEmail);
  if (userId) params.set('user_id', userId);
  const response = await fetch(`${API_BASE_URL}/api/reports/${reportId}?${params.toString()}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw await responseError(response);
  return await response.json();
}

// ---------------------------------------------------------------------------
// Chat History API (Neon PostgreSQL / Database)
// ---------------------------------------------------------------------------

export async function saveChatHistoryApi(payload: {
  user_email?: string;
  user_id?: string;
  session_id?: string;
  query: string;
  answer: string;
  language?: string;
  confidence?: string;
  grounded?: boolean;
  sources_json?: any;
}) {
  const response = await fetch(`${API_BASE_URL}/api/chat/history`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw await responseError(response);
  return await response.json();
}

export async function fetchChatHistoryApi(userEmail?: string, userId?: string) {
  const params = new URLSearchParams();
  if (userEmail) params.set('user_email', userEmail);
  if (userId) params.set('user_id', userId);
  const response = await fetch(`${API_BASE_URL}/api/chat/history?${params.toString()}`);
  if (!response.ok) throw await responseError(response);
  return await response.json();
}

export async function clearChatHistoryApi(userEmail?: string, userId?: string, historyId?: number) {
  const params = new URLSearchParams();
  if (userEmail) params.set('user_email', userEmail);
  if (userId) params.set('user_id', userId);
  if (historyId) params.set('history_id', String(historyId));
  const response = await fetch(`${API_BASE_URL}/api/chat/history?${params.toString()}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw await responseError(response);
  return await response.json();
}

