import type { ChatRequest, ChatResponse, HistoryResponse, Health } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public status: number, public detail: string) { super(detail); }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? res.statusText);
  }
  return res.json();
}

export const api = {
  sendChat: (body: ChatRequest) => request<ChatResponse>('/chat', { method: 'POST', body: JSON.stringify(body) }),
  clearSession: (sessionId: string) => request<void>(`/session/${sessionId}`, { method: 'DELETE' }),
  getHistory: (sessionId: string) => request<HistoryResponse>(`/session/${sessionId}/history`),
  health: () => request<Health>('/health'),
};
