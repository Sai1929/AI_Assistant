'use client';
import { useApp } from '@/lib/store';

export function ConnectionErrorBanner() {
  const setApiDown = useApp(s => s.setApiDown);
  return (
    <div className="mx-4 mt-3 flex items-start gap-3 border border-error rounded-sm bg-red-50 px-4 py-3">
      <span className="text-error font-ui font-semibold text-[13px] flex-1">
        ⚠ Cannot reach the assistant.{' '}
        <span className="font-mono text-[12px] text-ink-soft">$ uvicorn app.main:app --reload</span>
      </span>
      <button onClick={() => setApiDown(false)} className="text-[11px] font-ui font-semibold uppercase tracking-wide border border-error text-error px-3 py-1 rounded-sm hover:bg-red-100 transition-colors">Retry</button>
    </div>
  );
}
