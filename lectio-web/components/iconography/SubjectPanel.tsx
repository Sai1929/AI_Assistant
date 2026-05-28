'use client';
import { useState } from 'react';
import { Eyebrow } from '../ornament/Eyebrow';

const QUICK_SUBJECTS = ['Nativity', 'Good Shepherd', 'Baptism', 'The Cross', 'Annunciation', 'Dove descending'];
const STYLES = [
  { value: 'painterly', label: 'Painterly' },
  { value: 'mosaic', label: 'Byzantine mosaic' },
  { value: 'line', label: 'Line drawing' },
  { value: 'illuminated', label: 'Illuminated' },
] as const;

type StyleValue = typeof STYLES[number]['value'];

export function SubjectPanel({ onGenerate, isPending }: { onGenerate: (subject: string, style: string) => void; isPending: boolean }) {
  const [subject, setSubject] = useState('');
  const [style, setStyle] = useState<StyleValue>('painterly');
  const MAX = 500;

  return (
    <div className="w-[340px] shrink-0 bg-paper-deep border-r border-rule px-7 py-8 flex flex-col gap-5 overflow-auto">
      <div>
        <Eyebrow className="block mb-1">Iconography</Eyebrow>
        <h2 className="font-display text-[32px] font-medium text-ink mt-1">Compose an image.</h2>
        <p className="font-body italic text-[13px] text-muted leading-[1.55] mt-1">Two passes of safety review. No photorealistic deity depictions.</p>
      </div>

      <div>
        <Eyebrow className="block mb-2">Subject</Eyebrow>
        <div className="relative bg-card border border-rule rounded-sm p-3">
          <textarea
            value={subject}
            onChange={e => setSubject(e.target.value)}
            maxLength={MAX}
            rows={3}
            placeholder="Describe your subject…"
            className="w-full bg-transparent font-body text-[14px] text-ink leading-[1.55] outline-none resize-none placeholder:italic placeholder:text-muted"
          />
          {subject.length > 0 && <span className="absolute bottom-2 right-3 font-mono text-[10px] text-muted">{subject.length} / {MAX}</span>}
        </div>
      </div>

      <div>
        <Eyebrow className="block mb-2">Style</Eyebrow>
        <div className="space-y-1">
          {STYLES.map(s => (
            <button key={s.value} onClick={() => setStyle(s.value)} className={`w-full text-left px-3 py-2.5 rounded-sm font-display text-[15px] font-medium transition-colors border ${style === s.value ? 'bg-ink text-paper border-ink' : 'bg-transparent border-rule text-muted hover:text-ink'}`}>{s.label}</button>
          ))}
        </div>
      </div>

      <div>
        <Eyebrow className="block mb-2">Quick subjects</Eyebrow>
        <div className="flex flex-wrap gap-2">
          {QUICK_SUBJECTS.map(q => (
            <button key={q} onClick={() => setSubject(s => s ? s : q)} className="font-body italic text-[12px] text-ink-soft bg-card border border-rule rounded-pill px-2.5 py-1 hover:border-gold transition-colors">{q}</button>
          ))}
        </div>
      </div>

      <button
        onClick={() => subject.trim() && onGenerate(subject, style)}
        disabled={!subject.trim() || isPending}
        className="w-full py-3 bg-gold text-ink font-ui font-bold text-[12px] uppercase tracking-[0.2em] rounded-sm hover:opacity-90 transition-opacity disabled:opacity-40"
      >
        ✦ Compose image
      </button>
      <p className="font-body italic text-[11.5px] text-muted text-center -mt-3">Typically takes 12–18 seconds.</p>
    </div>
  );
}
