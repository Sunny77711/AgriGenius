import type { ChatRequest, ChatResponse, HealthResponse, SourcePassage } from './types';
import { mockChatResponse1, mockChatResponseHindi, mockHealthResponse } from './mockData';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const USE_MOCK = false;

export async function checkHealth(): Promise<HealthResponse> {
  if (USE_MOCK) {
    return new Promise((resolve) => setTimeout(() => resolve(mockHealthResponse), 500));
  }
  
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error('Failed to fetch health status');
  }
  return response.json();
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  if (USE_MOCK) {
    return new Promise((resolve) => {
      setTimeout(() => {
        if (request.query.match(/[\u0900-\u097F]/) || request.language === 'hi') {
          resolve(mockChatResponseHindi);
        } else {
          resolve(mockChatResponse1);
        }
      }, 1500);
    });
  }

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to get chat response');
  }
  
  return response.json();
}

export async function streamChatMessage(
  request: ChatRequest,
  onChunk: (chunk: string) => void,
  onSources: (sources: SourcePassage[]) => void,
  onError: (error: Error) => void,
  onComplete: () => void
) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to connect: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error('ReadableStream not supported in this browser.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split(/\r?\n\r?\n/);
      buffer = parts.pop() || '';

      for (const part of parts) {
        if (!part.trim()) continue;
        const lines = part.split(/\r?\n/);
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'metadata') {
                onSources(data.sources);
              } else if (data.type === 'chunk') {
                onChunk(data.content);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e, dataStr);
            }
          }
        }
      }
    }
    
    // Process any remaining buffer
    if (buffer.trim()) {
      const lines = buffer.split(/\r?\n/);
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6);
          try {
             const data = JSON.parse(dataStr);
             if (data.type === 'metadata') {
                 onSources(data.sources);
             } else if (data.type === 'chunk') {
                 onChunk(data.content);
             }
          } catch (e) {
             console.error('Error parsing SSE data in buffer:', e, dataStr);
          }
        }
      }
    }

    onComplete();
  } catch (err: any) {
    onError(err);
  }
}
