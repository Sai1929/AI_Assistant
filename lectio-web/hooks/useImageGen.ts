'use client';
import { useMutation } from '@tanstack/react-query';
import { api, ApiError } from '@/lib/api';
import { useApp } from '@/lib/store';
import { getSessionId } from '@/lib/session';
import type { ChatResponse } from '@/lib/types';
import { useState } from 'react';

export function useImageGen() {
  const { setApiDown } = useApp();
  const [result, setResult] = useState<ChatResponse | null>(null);

  const mutation = useMutation({
    mutationFn: async ({ subject, style }: { subject: string; style: string }) => {
      const session_id = getSessionId();
      const message = `[Iconography request, style: ${style}] ${subject}`;
      return api.sendChat({ session_id, message });
    },
    onSuccess: (res) => { setApiDown(false); setResult(res); },
    onError: (err: unknown) => {
      if (err instanceof ApiError && err.status === 0) setApiDown(true);
    },
  });

  return {
    result,
    isPending: mutation.isPending,
    generate: (subject: string, style: string) => mutation.mutate({ subject, style }),
    reset: () => setResult(null),
  };
}
