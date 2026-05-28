'use client';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

export type EvalSummary = { total: number; passed: number; failed: number; pass_rate: number; elapsed_seconds: number; by_category: Record<string, { total: number; passed: number }> };
export type EvalResult = { id: string; category: string; input: string; passed: boolean; refused: boolean; should_refuse: boolean; intent?: string; expected_intent?: string; details: string[] };
export type EvalData = { summary: EvalSummary; results: EvalResult[] };

export function useEvalResults() {
  const [refreshKey, setRefreshKey] = useState(0);
  const query = useQuery<EvalData | null>({
    queryKey: ['eval-results', refreshKey],
    queryFn: async () => {
      try {
        const res = await fetch('/api/eval-results');
        if (!res.ok) return null;
        return res.json();
      } catch { return null; }
    },
    staleTime: 30_000,
  });
  return { ...query, refresh: () => setRefreshKey(k => k + 1) };
}
