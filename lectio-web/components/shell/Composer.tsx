'use client';
import { useRef, useEffect, useState } from 'react';
import { Cross } from '../ornament/Cross';

export function Composer({ value, onChange, onSubmit, placeholder = 'Ask of scripture…', isSending = false }: {
  value: string; onChange: (v: string) => void; onSubmit: () => void; placeholder?: string; isSending?: boolean;
}) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [rows] = useState(1);
  const MAX = 2000;

  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = 'auto';
      const scrollH = ref.current.scrollHeight;
      ref.current.style.height = `${Math.min(scrollH, 120)}px`;
    }
  }, [value]);

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (value.trim() && !isSending) onSubmit(); }
  }

  return (
    <div>
      <div className="flex items-start gap-3 bg-card border border-rule rounded-sm px-4 py-3 focus-within:border-gold transition-colors">
        <Cross size={15} color="#B8881A" strokeWidth={2} className="mt-1 shrink-0" />
        <textarea
          ref={ref}
          value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={handleKey}
          placeholder={placeholder}
          maxLength={MAX}
          rows={rows}
          disabled={isSending}
          className="flex-1 resize-none bg-transparent font-body text-[15.5px] text-ink placeholder:italic placeholder:text-muted outline-none leading-relaxed"
          style={{ maxHeight: 120 }}
        />
        <span className="font-mono text-[10.5px] text-muted mt-1 shrink-0">↵</span>
      </div>
      <div className="flex justify-between mt-1.5 px-1">
        {value.length > 1500
          ? <span className="font-mono text-[11px] text-warning">{value.length} / {MAX}</span>
          : <span className="font-body italic text-[11px] text-muted">Every citation is verified against three translations.</span>
        }
        <span className="font-body italic text-[11px] text-muted">Shift + Return for a new line</span>
      </div>
    </div>
  );
}
