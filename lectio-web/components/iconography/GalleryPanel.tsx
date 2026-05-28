'use client';
import { useState, useEffect } from 'react';
import { Download, Check } from 'lucide-react';
import { Eyebrow } from '../ornament/Eyebrow';
import type { ChatResponse } from '@/lib/types';

const LOADING_CAPTIONS = [
  'Reviewing the prompt for safety…',
  'Composing the image…',
  'Reviewing the image content…',
];

export function GalleryPanel({ result, isPending, onVariation }: { result: ChatResponse | null; isPending: boolean; onVariation: () => void }) {
  const [captionIdx, setCaptionIdx] = useState(0);

  useEffect(() => {
    if (!isPending) return;
    const interval = setInterval(() => setCaptionIdx(i => Math.min(i + 1, LOADING_CAPTIONS.length - 1)), 3000);
    return () => clearInterval(interval);
  }, [isPending]);

  function handleDownload() {
    if (!result?.image_b64) return;
    const a = document.createElement('a');
    a.href = `data:image/png;base64,${result.image_b64}`;
    a.download = 'lectio-image.png';
    a.click();
  }

  return (
    <div className="flex-1 px-9 py-8 overflow-auto">
      <div className="flex items-center justify-between mb-4">
        <Eyebrow>Latest</Eyebrow>
        {result?.image_b64 && (
          <div className="flex items-center gap-1.5">
            <Check size={12} color="#3F6B3A" />
            <span className="eyebrow text-success">Two passes safe</span>
          </div>
        )}
      </div>

      {isPending && (
        <div className="bg-card border border-rule rounded-sm p-8 flex flex-col items-center gap-4">
          <div className="w-full bg-rule rounded-full h-1.5 overflow-hidden">
            <div className="h-full bg-gold animate-pulse w-2/3" />
          </div>
          <p className="font-body italic text-[13px] text-muted">{LOADING_CAPTIONS[captionIdx]}</p>
        </div>
      )}

      {!isPending && !result && (
        <div className="border-2 border-dashed border-rule rounded-sm bg-paper-deep flex flex-col items-center justify-center py-20 gap-3">
          <p className="font-display text-[22px] text-muted">Your composed image will appear here.</p>
          <p className="font-body italic text-[12.5px] text-muted">Begin by writing a subject or choosing a quick prompt.</p>
        </div>
      )}

      {!isPending && result && (
        <>
          {result.image_b64 ? (
            <div className="bg-card border border-rule rounded-sm p-3">
              <img src={`data:image/png;base64,${result.image_b64}`} alt="Generated Christian art" className="w-full rounded-hairline" style={{ maxHeight: 380, objectFit: 'contain' }} />
            </div>
          ) : (
            <div className="border-l-2 border-sienna pl-5 py-4">
              <Eyebrow color="sienna" className="block mb-2">Image not generated</Eyebrow>
              <p className="font-body text-[15.5px] text-ink leading-[1.7]">{result.response}</p>
            </div>
          )}
          {result.image_b64 && (
            <div className="flex gap-6 mt-4">
              <button onClick={handleDownload} className="flex items-center gap-1.5 text-[11px] font-ui font-semibold uppercase tracking-wide text-muted hover:text-ink transition-colors"><Download size={12} />Download PNG</button>
              <button onClick={onVariation} className="text-[11px] font-ui font-semibold uppercase tracking-wide text-muted hover:text-ink transition-colors">Make a variation</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
