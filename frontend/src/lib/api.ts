import type { ChatRequest, ChatResponse, HealthResponse } from './types';
import { mockChatResponse1, mockChatResponseHindi, mockHealthResponse } from './mockData';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const USE_MOCK = true; // Set to false when backend is ready

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
        // Simple mock logic based on language hint
        if (request.query.match(/[\u0900-\u097F]/) || request.language === 'hi') {
          resolve(mockChatResponseHindi);
        } else {
          resolve(mockChatResponse1);
        }
      }, 1500); // Simulate network latency + generation time
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
