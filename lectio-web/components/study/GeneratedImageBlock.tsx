import { Check, Download } from 'lucide-react';
import { Eyebrow } from '../ornament/Eyebrow';

export function GeneratedImageBlock({ src, rewrittenPrompt, onDownload, onVariation }: {
  src: string; rewrittenPrompt: string; onDownload: () => void; onVariation: () => void;
}) {
  return (
    <div className="my-4 bg-card border border-rule rounded-sm p-3">
      <img src={src} alt={rewrittenPrompt} className="w-full rounded-hairline" style={{ maxHeight: 320, objectFit: 'contain' }} />
      <p className="font-body italic text-[13.5px] text-ink-soft mt-3 leading-[1.55]">&ldquo;{rewrittenPrompt}&rdquo;</p>
      <div className="flex items-center gap-4 mt-3">
        <span className="flex items-center gap-1 text-[11px] font-ui font-semibold uppercase tracking-wide text-success"><Check size={12} />Prompt safety</span>
        <span className="flex items-center gap-1 text-[11px] font-ui font-semibold uppercase tracking-wide text-success"><Check size={12} />Content review</span>
        <div className="ml-auto flex gap-4">
          <button onClick={onDownload} className="text-[11px] font-ui font-semibold uppercase tracking-wide text-muted hover:text-ink transition-colors flex items-center gap-1"><Download size={11} />Download</button>
          <button onClick={onVariation} className="text-[11px] font-ui font-semibold uppercase tracking-wide text-muted hover:text-ink transition-colors">New variation</button>
        </div>
      </div>
    </div>
  );
}
