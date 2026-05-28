'use client';
import { useState } from 'react';
import { Eyebrow } from '../ornament/Eyebrow';

const QUICK_SUBJECTS = ['Nativity', 'Good Shepherd', 'Baptism', 'The Cross', 'Annunciation', 'Dove descending'];
const STYLES = [
  { value: 'painterly',    label: 'Painterly' },
  { value: 'mosaic',       label: 'Byzantine mosaic' },
  { value: 'line',         label: 'Line drawing' },
  { value: 'illuminated',  label: 'Illuminated' },
] as const;

type StyleValue = typeof STYLES[number]['value'];

export function SubjectPanel({ onGenerate, isPending }: {
  onGenerate: (subject: string, style: string) => void;
  isPending: boolean;
}) {
  const [subject, setSubject] = useState('');
  const [style, setStyle] = useState<StyleValue>('painterly');
  const MAX = 500;

  function handleQuickSubject(q: string) {
    setSubject(q);
  }

  function handleGenerate() {
    const v = subject.trim();
    if (!v || isPending) return;
    onGenerate(v, style);
  }

  return (
    <div className="w-[320px] shrink-0 bg-paper-deep border-r border-rule px-6 py-7 flex flex-col gap-5 overflow-y-auto">
      {/* Header */}
      <div>
        <Eyebrow className="block mb-1">Iconography</Eyebrow>
        <h2 className="font-display text-[28px] font-medium text-ink mt-1 leading-tight">Compose an image.</h2>
        <p className="font-body italic text-[12.5px] text-muted leading-snug mt-1">
          Two passes of safety review. No photorealistic deity depictions.
        </p>
      </div>

      {/* Subject input */}
      <div>
        <Eyebrow className="block mb-2">Subject</Eyebrow>
        <div className={`relative bg-card border rounded-sm p-3 transition-colors ${subject ? 'border-gold' : 'border-rule'}`}>
          <textarea
            value={subject}
            onChange={e => setSubject(e.target.value)}
            maxLength={MAX}
            rows={3}
            disabled={isPending}
            placeholder="Describe your subject…"
            className="w-full bg-transparent font-body text-[14px] text-ink leading-relaxed outline-none resize-none placeholder:italic placeholder:text-muted disabled:opacity-60"
          />
          {subject.length > 0 && (
            <span className="absolute bottom-2 right-3 font-mono text-[10px] text-muted">{subject.length} / {MAX}</span>
          )}
        </div>
      </div>

      {/* Quick subjects */}
      <div>
        <Eyebrow className="block mb-2">Quick subjects</Eyebrow>
        <div className="flex flex-wrap gap-2">
          {QUICK_SUBJECTS.map(q => (
            <button
              key={q}
              onClick={() => handleQuickSubject(q)}
              disabled={isPending}
              className={`font-body italic text-[12px] bg-card border rounded-pill px-2.5 py-1 transition-colors disabled:opacity-40 ${subject === q ? 'border-gold text-gold' : 'border-rule text-ink-soft hover:border-gold'}`}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Style selector */}
      <div>
        <Eyebrow className="block mb-2">Style</Eyebrow>
        <div className="space-y-1">
          {STYLES.map(s => (
            <button
              key={s.value}
              onClick={() => setStyle(s.value)}
              disabled={isPending}
              className={`w-full text-left px-3 py-2 rounded-sm font-display text-[14px] font-medium transition-colors border disabled:opacity-40 ${
                style === s.value
                  ? 'bg-ink text-paper border-ink ring-2 ring-gold ring-offset-1'
                  : 'bg-transparent border-rule text-muted hover:text-ink hover:border-ink-soft'
              }`}
            >
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${style === s.value ? 'bg-gold' : 'bg-transparent border border-rule'}`} />
                {s.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Generate button */}
      <button
        onClick={handleGenerate}
        disabled={!subject.trim() || isPending}
        className="w-full py-3 bg-gold text-ink font-ui font-bold text-[12px] uppercase tracking-[0.18em] rounded-sm hover:opacity-90 transition-opacity disabled:opacity-40 flex items-center justify-center gap-2"
      >
        {isPending ? (
          <>
            <svg className="animate-spin" width="14" height="14" viewBox="0 0 48 48" fill="none">
              <rect x="21" y="4"  width="6" height="40" rx="3" fill="currentColor" />
              <rect x="4"  y="17" width="40" height="6" rx="3" fill="currentColor" />
            </svg>
            Composing…
          </>
        ) : (
          '✦ Compose image'
        )}
      </button>

      <p className="font-body italic text-[11px] text-muted text-center -mt-3">
        {isPending ? 'Processing — typically 8–15 seconds' : 'Typically takes 8–15 seconds.'}
      </p>
    </div>
  );
}
