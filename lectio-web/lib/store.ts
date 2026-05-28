import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Tradition, Message } from './types';

type AppState = {
  sessionId: string;
  tradition: Tradition;
  messages: Message[];
  apiDown: boolean;
  lastError: string | null;
  setTradition: (t: Tradition) => void;
  setSessionId: (id: string) => void;
  appendMessage: (m: Message) => void;
  clearMessages: () => void;
  setApiDown: (v: boolean) => void;
  setLastError: (e: string | null) => void;
};

export const useApp = create<AppState>()(
  persist(
    (set) => ({
      sessionId: '',
      tradition: 'auto',
      messages: [],
      apiDown: false,
      lastError: null,
      setTradition: (tradition) => set({ tradition }),
      setSessionId: (sessionId) => set({ sessionId }),
      appendMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
      clearMessages: () => set({ messages: [] }),
      setApiDown: (apiDown) => set({ apiDown }),
      setLastError: (lastError) => set({ lastError }),
    }),
    { name: 'lectio:app', partialize: (s) => ({ tradition: s.tradition }) },
  ),
);
