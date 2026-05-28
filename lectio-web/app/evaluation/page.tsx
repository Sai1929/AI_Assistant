'use client';
import { AppShell } from '@/components/shell/AppShell';
import { EvalDashboard } from '@/components/evaluation/EvalDashboard';
import { Fleuron } from '@/components/ornament/Fleuron';
import { Eyebrow } from '@/components/ornament/Eyebrow';
import { useEvalResults } from '@/hooks/useEvalResults';
import { RefreshCw } from 'lucide-react';

export default function EvaluationPage() {
  const { data, isLoading, refresh } = useEvalResults();

  return (
    <AppShell activeTab="evaluation">
      <div className="h-full overflow-auto">
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <RefreshCw size={20} className="animate-spin text-muted" />
          </div>
        )}
        {!isLoading && !data && (
          <div className="flex flex-col items-center justify-center h-full gap-6 max-w-[640px] mx-auto px-8">
            <Fleuron width={80} />
            <Eyebrow className="text-center">No evaluation results</Eyebrow>
            <p className="font-body text-[15px] text-ink-soft text-center">Run the evaluation script to generate results.</p>
            <div className="w-full space-y-3">
              <div className="bg-card border border-rule rounded-sm p-5">
                <p className="font-mono text-[13px] text-ink">$ python scripts/run_eval.py</p>
                <p className="font-mono text-[12px] text-muted mt-2"># Fast mode — no API keys needed.</p>
                <p className="font-mono text-[12px] text-muted"># Tests regex pre-screen + intent classifier</p>
              </div>
              <div className="bg-card border border-rule rounded-sm p-5">
                <p className="font-mono text-[13px] text-ink">$ python scripts/run_eval.py --full</p>
              </div>
            </div>
            <button onClick={refresh} className="flex items-center gap-2 border border-rule rounded-sm px-5 py-2 text-[11px] font-ui font-semibold uppercase tracking-wide text-ink hover:bg-paper-deep transition-colors">
              <RefreshCw size={12} />Refresh
            </button>
          </div>
        )}
        {!isLoading && data && <EvalDashboard data={data} onRefresh={refresh} />}
      </div>
    </AppShell>
  );
}
