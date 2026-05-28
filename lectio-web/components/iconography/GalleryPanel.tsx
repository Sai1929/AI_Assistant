'use client';
import { useState, useEffect } from 'react';
import { Download, Check } from 'lucide-react';
import { Eyebrow } from '../ornament/Eyebrow';
import type { ChatResponse } from '@/lib/types';

const STAGES = [
  { label: 'Gate 1 · Reviewing prompt for safety…', pct: 20 },
  { label: 'Gate 1 · Rewriting for reverence…',    pct: 35 },
  { label: 'Gate 2 · Composing image…',             pct: 60 },
  { label: 'Gate 2 · Composing image…',             pct: 75 },
  { label: 'Gate 3 · Reviewing image content…',     pct: 90 },
  { label: 'Gate 3 · Final safety check…',          pct: 95 },
];

export function GalleryPanel({ result, isPending, onVariation }: {
  result: ChatResponse | null;
  isPending: boolean;
  onVariation: () => void;
}) {
  const [stageIdx, setStageIdx] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!isPending) { setStageIdx(0); setElapsed(0); return; }
    const tick = setInterval(() => setElapsed(s => s + 1), 1000);
    const advance = setInterval(() => setStageIdx(i => Math.min(i + 1, STAGES.length - 1)), 3500);
    return () => { clearInterval(tick); clearInterval(advance); };
  }, [isPending]);

  const mime = result?.image_mime_type ?? 'image/jpeg';
  const ext  = mime === 'image/png' ? 'png' : 'jpg';

  function handleDownload() {
    if (!result?.image_b64) return;
    const a = document.createElement('a');
    a.href = `data:${mime};base64,${result.image_b64}`;
    a.download = `lectio-image.${ext}`;
    a.click();
  }

  const stage = STAGES[stageIdx];

  return (
    <div className="flex-1 px-9 py-8 overflow-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <Eyebrow>{isPending ? 'Composing…' : 'Latest'}</Eyebrow>
        {result?.image_b64 && !isPending && (
          <div className="flex items-center gap-1.5">
            <Check size={12} color="#3F6B3A" />
            <span className="eyebrow text-success">Two passes safe</span>
          </div>
        )}
      </div>

      {/* Loading state */}
      {isPending && (
        <div className="bg-card border border-rule rounded-md p-8 flex flex-col gap-5">
          {/* Animated cross spinner */}
          <div className="flex justify-center">
            <svg
              width="48" height="48" viewBox="0 0 48 48" fill="none"
              className="animate-spin"
              style={{ animationDuration: '2s' }}
            >
              <rect x="21" y="4"  width="6" height="40" rx="3" fill="#B8881A" opacity="0.9" />
              <rect x="4"  y="17" width="40" height="6" rx="3" fill="#B8881A" opacity="0.9" />
            </svg>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-rule rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gold rounded-full transition-all duration-700"
              style={{ width: `${stage.pct}%` }}
            />
          </div>

          {/* Stage label */}
          <div className="text-center">
            <p className="font-body italic text-[13px] text-muted">{stage.label}</p>
            <p className="font-mono text-[11px] text-muted/60 mt-1">{elapsed}s elapsed · typically 8–15s</p>
          </div>

          {/* Stage dots */}
          <div className="flex justify-center gap-2">
            {STAGES.map((_, i) => (
              <span
                key={i}
                className={`w-1.5 h-1.5 rounded-full transition-colors duration-300 ${i <= stageIdx ? 'bg-gold' : 'bg-rule'}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!isPending && !result && (
        <div className="border-2 border-dashed border-rule rounded-md bg-paper-deep flex flex-col items-center justify-center py-20 gap-3">
          <svg width="40" height="40" viewBox="0 0 48 48" fill="none" opacity="0.25">
            <rect x="21" y="4"  width="6" height="40" rx="3" fill="#14283D" />
            <rect x="4"  y="17" width="40" height="6" rx="3" fill="#14283D" />
          </svg>
          <p className="font-display text-[20px] text-muted">Your composed image will appear here.</p>
          <p className="font-body italic text-[12.5px] text-muted">Choose a subject or quick prompt, then compose.</p>
        </div>
      )}

      {/* Result */}
      {!isPending && result && (
        <>
          {result.image_b64 ? (
            <div className="bg-card border border-rule rounded-md p-3">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`data:${mime};base64,${result.image_b64}`}
                alt="Generated Christian art"
                className="w-full rounded-sm"
                style={{ maxHeight: 420, objectFit: 'contain' }}
              />
            </div>
          ) : (
            <div className="border-l-2 border-sienna pl-5 py-4">
              <Eyebrow color="sienna" className="block mb-2">Image not generated</Eyebrow>
              <p className="font-body text-[15px] text-ink leading-relaxed">{result.response}</p>
            </div>
          )}

          {result.image_b64 && (
            <div className="flex gap-6 mt-4">
              <button
                onClick={handleDownload}
                className="flex items-center gap-1.5 text-[11px] font-ui font-semibold uppercase tracking-wide text-muted hover:text-ink transition-colors"
              >
                <Download size={12} />
                Download {ext.toUpperCase()}
              </button>
              <button
                onClick={onVariation}
                className="text-[11px] font-ui font-semibold uppercase tracking-wide text-muted hover:text-ink transition-colors"
              >
                Make a variation →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
