'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
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
  const router = useRouter();
  const [showClear, setShowClear] = useState(false);
  const [copied, setCopied] = useState(false);
  const [sessionId, setSessionIdLocal] = useState('');
  const hint = getLiturgicalHint();

  useEffect(() => {
    setSessionIdLocal(getSessionId());
  }, []);

  function handleCopy() {
    navigator.clipboard.writeText(sessionId);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  async function handleClear() {
    try { await api.clearSession(sessionId); } catch {}
    const newId = rotateSessionId();
    setSessionId(newId);
    setSessionIdLocal(newId);
    clearMessages();
    setShowClear(false);
  }

  return (
    <>
      <aside className="flex flex-col w-56 shrink-0 h-full bg-paper-deep border-r border-rule px-4 py-5 overflow-y-auto">
        {/* Wordmark */}
        <div className="mb-5">
          <div className="flex items-center gap-2 mb-1">
            <Cross size={16} color="#B8881A" strokeWidth={2.5} />
            <span className="font-display text-[22px] font-semibold text-ink leading-none">Lectio</span>
          </div>
          <p className="font-body italic text-[11.5px] text-muted leading-snug">A scripture-grounded study companion.</p>
        </div>

        {/* Today's Reading */}
        <div className="bg-card border border-rule rounded-md p-3 mb-5">
          <Eyebrow className="block mb-1">Today&apos;s reading</Eyebrow>
          <p className="font-display text-[17px] font-medium text-ink mb-1">Psalm 23</p>
          <p className="font-body italic text-[11px] text-muted leading-snug">&ldquo;The Lord is my shepherd; I shall not want.&rdquo;</p>
          <button
            onClick={() => router.push('/study?q=' + encodeURIComponent('Walk me through Psalm 23 verse by verse and what comfort it offers.'))}
            className="mt-2 w-full text-[11px] font-ui font-semibold uppercase tracking-wide bg-ink text-paper rounded-sm py-1.5 hover:bg-ink-soft transition-colors"
          >
            Read with me →
          </button>
        </div>

        {/* Tradition */}
        <div className="mb-5">
          <Eyebrow className="block mb-2">Tradition</Eyebrow>
          <div className="space-y-1">
            {traditions.map(t => (
              <button
                key={t.value}
                onClick={() => setTradition(t.value)}
                className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-sm text-[12.5px] font-body transition-colors ${tradition === t.value ? 'bg-card border border-rule text-ink' : 'text-muted hover:text-ink-soft'}`}
              >
                <span className={`w-2 h-2 rounded-full border flex-shrink-0 ${tradition === t.value ? 'bg-gold border-gold' : 'border-muted'}`} />
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Liturgical hint */}
        <p className="font-body italic text-[11px] text-muted mb-auto" suppressHydrationWarning>⊕ Today: {hint.label}</p>

        {/* Session footer */}
        <div className="pt-3 border-t border-rule mt-3">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-mono text-[10.5px] text-muted truncate flex-1">{sessionId.slice(0, 8)}…</span>
            <button onClick={handleCopy} className="text-muted hover:text-ink transition-colors" aria-label="Copy session ID">
              <Copy size={12} />
            </button>
            {copied && <span className="text-[10px] text-success">Copied</span>}
          </div>
          <button
            onClick={() => setShowClear(true)}
            className="w-full flex items-center justify-center gap-1.5 border border-error text-error text-[11px] font-ui font-semibold uppercase tracking-wide rounded-sm py-1.5 hover:bg-red-50 transition-colors"
          >
            <Trash2 size={11} />
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
