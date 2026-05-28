'use client';
import { useMutation } from '@tanstack/react-query';
import { nanoid } from 'nanoid';
import { api, ApiError } from '@/lib/api';
import { useApp } from '@/lib/store';
import { getSessionId } from '@/lib/session';
import type { Tradition } from '@/lib/types';

function buildMessage(raw: string, tradition: Tradition): string {
  if (tradition === 'auto') return raw;
  const map = { catholic: 'Catholic', protestant: 'Protestant', orthodox: 'Orthodox' } as const;
  return `[Denomination preference: ${map[tradition]}] ${raw}`;
}

function nowTime() {
  return new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

export function useChat() {
  const { messages, appendMessage, tradition, setApiDown, setLastError } = useApp();

  const mutation = useMutation({
    mutationFn: async (rawInput: string) => {
      const session_id = getSessionId();
      const message = buildMessage(rawInput, tradition);
      appendMessage({ id: nanoid(), role: 'user', content: rawInput, time: nowTime() });
      return api.sendChat({ session_id, message });
    },
    onSuccess: (res) => {
      setApiDown(false);
      appendMessage({ id: nanoid(), role: 'assistant', content: res.response ?? '', time: nowTime(), meta: res });
    },
    onError: (err: unknown) => {
      if (err instanceof ApiError && err.status === 0) setApiDown(true);
      setLastError(err instanceof Error ? err.message : 'Unknown error');
    },
  });

  return {
    messages,
    isPending: mutation.isPending,
    send: (input: string) => mutation.mutate(input),
  };
}
