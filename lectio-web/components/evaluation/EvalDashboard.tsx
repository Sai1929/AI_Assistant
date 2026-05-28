'use client';
import { RefreshCw } from 'lucide-react';
import { Eyebrow } from '../ornament/Eyebrow';
import { Fleuron } from '../ornament/Fleuron';
import type { EvalData } from '@/hooks/useEvalResults';

function PassRateColor(rate: number) {
  if (rate >= 0.8) return 'text-success';
  if (rate >= 0.6) return 'text-warning';
  return 'text-error';
}

export function EvalDashboard({ data, onRefresh, isRunning }: { data: EvalData; onRefresh: () => void; isRunning?: boolean }) {
  const { summary, results } = data;
  const cats = Object.entries(summary.by_category);

  return (
    <div className="max-w-4xl mx-auto px-14 py-8">
      {/* Masthead */}
      <div className="flex items-end justify-between pb-5 border-b border-rule mb-6">
        <div>
          <Eyebrow className="block mb-1">{summary.total} prompts · {cats.length} categories</Eyebrow>
          <h1 className="font-display text-[38px] font-medium text-ink">Evaluation</h1>
          <p className="font-body italic text-[13px] text-muted mt-1">
            {isRunning ? 'Running evaluation… ~2 minutes' : `Last run in ${summary.elapsed_seconds}s`}
          </p>
        </div>
        <button
          onClick={onRefresh}
          disabled={isRunning}
          className="flex items-center gap-2 border border-rule bg-card rounded-sm px-4 py-2 text-[11px] font-ui font-semibold uppercase tracking-wide text-ink hover:bg-paper-deep transition-colors disabled:opacity-40"
        >
          <RefreshCw size={12} className={isRunning ? 'animate-spin' : ''} />
          {isRunning ? 'Running…' : 'Re-run eval'}
        </button>
      </div>

      {/* Metric row */}
      <div className="grid grid-cols-3 gap-0 border border-rule rounded-sm mb-8">
        {[
          { label: 'Pass rate', value: `${(summary.pass_rate * 100).toFixed(1)}%`, cls: PassRateColor(summary.pass_rate) },
          { label: 'Passed', value: `${summary.passed}`, unit: `/ ${summary.total}`, cls: 'text-ink' },
          { label: 'Failed', value: `${summary.failed}`, cls: 'text-warning' },
        ].map((m, i) => (
          <div key={i} className={`px-7 py-6 ${i > 0 ? 'border-l border-rule' : ''}`}>
            <Eyebrow className="block mb-2">{m.label}</Eyebrow>
            <div className="flex items-baseline gap-1">
              <span className={`font-display text-[52px] font-medium leading-none ${m.cls}`}>{m.value}</span>
              {m.unit && <span className="font-display text-[22px] text-muted">{m.unit}</span>}
            </div>
          </div>
        ))}
      </div>

      {/* By category */}
      <div className="mb-8">
        <Eyebrow className="block mb-4">By category</Eyebrow>
        <div className="border border-rule rounded-sm divide-y divide-rule">
          {cats.map(([cat, stats]) => {
            const rate = stats.passed / stats.total;
            const fillColor = rate >= 0.8 ? '#3F6B3A' : rate >= 0.6 ? '#A66218' : '#9B3232';
            return (
              <div key={cat} className="grid items-center px-5 py-3" style={{ gridTemplateColumns: '200px 1fr 70px 80px' }}>
                <span className="font-display text-[16px] font-semibold text-ink">{cat.replace(/_/g, ' ')}</span>
                <div className="mx-4 h-1.5 bg-rule rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${rate * 100}%`, backgroundColor: fillColor }} />
                </div>
                <span className="font-mono text-[12px] text-muted text-right">{stats.passed}/{stats.total}</span>
                <span className="font-mono text-[12px] text-right" style={{ color: fillColor }}>{(rate * 100).toFixed(0)}%</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Detailed results table */}
      <div>
        <Eyebrow className="block mb-4">Detailed results</Eyebrow>
        <div className="border border-rule rounded-sm overflow-hidden">
          <table className="w-full text-left">
            <thead className="border-b border-rule bg-paper-deep">
              <tr>
                {['ID', 'Category', 'Prompt', 'Pass', 'Detected intent'].map(h => (
                  <th key={h} className="px-4 py-2.5 eyebrow">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-rule">
              {results.map(r => (
                <tr key={r.id} className="hover:bg-paper-deep transition-colors">
                  <td className="px-4 py-2.5 font-mono text-[11px] text-muted">{r.id}</td>
                  <td className="px-4 py-2.5 font-body italic text-[13px] text-ink-soft">{r.category}</td>
                  <td className="px-4 py-2.5 font-display text-[15px] text-ink max-w-[280px] truncate">{r.input}</td>
                  <td className="px-4 py-2.5">
                    <span className={`font-ui text-[11px] font-bold uppercase tracking-wide ${r.passed ? 'text-success' : 'text-error'}`}>
                      {r.passed ? '✓ Pass' : '✕ Fail'}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 font-body italic text-[13px] text-ink-soft">{r.intent ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
