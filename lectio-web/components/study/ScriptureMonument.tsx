import { Check, AlertTriangle } from 'lucide-react';

export function ScriptureMonument({ verse, reference, translation, verified }: {
  verse: string; reference: string; translation: string; verified: boolean;
}) {
  const first = verse[0];
  const rest = verse.slice(1);
  return (
    <div className="my-6 bg-card border border-rule rounded-sm p-6">
      <p className="font-body italic text-[22px] text-ink leading-[1.55]">
        <span className="float-left font-display text-[64px] font-semibold text-gold leading-[0.8] mr-2 mt-1">{first}</span>
        {rest}
      </p>
      <div className="clear-both pt-3 mt-3 border-t border-rule flex items-center gap-3">
        <span className="font-display text-[16px] font-semibold text-ink">— {reference}</span>
        <span className="font-mono text-[10.5px] text-muted border border-rule rounded-hairline px-1.5 py-0.5">{translation}</span>
        <span className="ml-auto flex items-center gap-1.5">
          {verified
            ? <><span className="w-3.5 h-3.5 rounded-full bg-success flex items-center justify-center"><Check size={8} color="white" strokeWidth={3} /></span><span className="eyebrow text-success">Verified</span></>
            : <><span className="w-3.5 h-3.5 rounded-full bg-sienna flex items-center justify-center"><AlertTriangle size={8} color="white" strokeWidth={3} /></span><span className="eyebrow text-sienna">Unverified</span></>
          }
        </span>
      </div>
    </div>
  );
}
