'use client';
import { useState } from 'react';
import { Trash2, Copy } from 'lucide-react';
import { Cross } from '../ornament/Cross';
import { Eyebrow } from '../ornament/Eyebrow';
import { useApp } from '@/lib/store';
import { getSessionId, rotateSessionId } from '@/lib/session';
import { api } from '@/lib/api';
import { getLiturgicalHint } from '@/lib/liturgical-calendar';
import { ConfirmModal } from '../overlays/ConfirmModal';
import type { Tradition } from '@/lib/types';

const traditions: { value: Tradition; label: string }[] = [
  { value: 'auto', label: 'Auto-detect' },
  { value: 'catholic', label: 'Catholic' },
  { value: 'protestant', label: 'Protestant' },
  { value: 'orthodox', label: 'Orthodox' },
];

export function Sidebar() {
  const { tradition, setTradition, setSessionId, clearMessages } = useApp();
  const [showClear, setShowClear] = useState(false);
  const [copied, setCopied] = useState(false);
  const sessionId = getSessionId();
  const hint = getLiturgicalHint();

  function handleCopy() {
    navigator.clipboard.writeText(sessionId);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  async function handleClear() {
    try { await api.clearSession(sessionId); } catch {}
    const newId = rotateSessionId();
    setSessionId(newId);
    clearMessages();
    setShowClear(false);
  }

  return (
    <>
      <aside className="flex flex-col w-60 shrink-0 h-full bg-paper-deep border-r border-rule px-5 py-6">
        {/* Wordmark */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <Cross size={18} color="#B8881A" strokeWidth={2.5} />
            <span className="font-display text-[26px] font-semibold text-ink leading-none">Lectio</span>
          </div>
          <p className="font-body italic text-[12.5px] text-muted leading-snug">A scripture-grounded study companion.</p>
        </div>

        {/* Today's Reading */}
        <div className="bg-card border border-rule rounded-md p-4 mb-6">
          <Eyebrow className="block mb-1">Today&apos;s reading</Eyebrow>
          <p className="font-display text-[19px] font-medium text-ink mb-1">Psalm 23</p>
          <p className="font-body italic text-[12px] text-muted leading-snug">&ldquo;The Lord is my shepherd; I shall not want.&rdquo;</p>
          <button className="mt-3 w-full text-[11.5px] font-ui font-semibold uppercase tracking-wide bg-ink text-paper rounded-sm py-1.5 hover:bg-ink-soft transition-colors">
            Read with me →
          </button>
        </div>

        {/* Tradition */}
        <div className="mb-6">
          <Eyebrow className="block mb-2">Tradition</Eyebrow>
          <div className="space-y-1">
            {traditions.map(t => (
              <button
                key={t.value}
                onClick={() => setTradition(t.value)}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-sm text-[13px] font-body transition-colors ${tradition === t.value ? 'bg-card border border-rule text-ink' : 'text-muted hover:text-ink-soft'}`}
              >
                <span className={`w-2 h-2 rounded-full border ${tradition === t.value ? 'bg-gold border-gold' : 'border-muted'}`} />
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Liturgical hint */}
        <p className="font-body italic text-[12px] text-muted mb-auto">⊕ Today: {hint.label}</p>

        {/* Session footer */}
        <div className="pt-4 border-t border-rule mt-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="font-mono text-[11px] text-muted truncate flex-1">{sessionId.slice(0, 8)}…</span>
            <button onClick={handleCopy} className="text-muted hover:text-ink transition-colors" aria-label="Copy session ID">
              <Copy size={13} />
            </button>
            {copied && <span className="text-[10px] text-success">Copied</span>}
          </div>
          <button
            onClick={() => setShowClear(true)}
            className="w-full flex items-center justify-center gap-2 border border-error text-error text-[11px] font-ui font-semibold uppercase tracking-wide rounded-sm py-2 hover:bg-red-50 transition-colors"
          >
            <Trash2 size={12} />
            Clear conversation
          </button>
        </div>
      </aside>

      {showClear && (
        <ConfirmModal
          title="Clear this session?"
          body="All conversation history will be deleted. Verse citations and any generated images won't be recoverable."
          confirmLabel="Clear session"
          onConfirm={handleClear}
          onCancel={() => setShowClear(false)}
        />
      )}
    </>
  );
}
