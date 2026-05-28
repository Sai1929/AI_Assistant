'use client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export type EvalSummary = {
  total: number; passed: number; failed: number;
  pass_rate: number; elapsed_seconds: number;
  by_category: Record<string, { total: number; passed: number }>;
};
export type EvalResult = {
  id: string; category: string; input: string;
  passed: boolean; refused: boolean; should_refuse: boolean;
  intent?: string; expected_intent?: string; details: string[];
};
export type EvalData = { summary: EvalSummary; results: EvalResult[] };

const QK = ['eval-results'];

export function useEvalResults() {
  const qc = useQueryClient();

  const query = useQuery<EvalData | null>({
    queryKey: QK,
    queryFn: async () => {
      try {
        const res = await fetch('/api/eval-results');
        if (!res.ok) return null;
        return res.json();
      } catch { return null; }
    },
    staleTime: 60_000,
  });

  const runMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/eval-results', { method: 'POST' });
      if (!res.ok) throw new Error('Eval run failed');
      return res.json() as Promise<EvalData>;
    },
    onSuccess: (data) => {
      qc.setQueryData(QK, data);
    },
  });

  return {
    data: query.data ?? null,
    isLoading: query.isLoading,
    isRunning: runMutation.isPending,
    runEval: () => runMutation.mutate(),
    refresh: () => qc.invalidateQueries({ queryKey: QK }),
  };
}
