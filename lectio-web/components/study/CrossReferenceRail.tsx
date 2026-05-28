import { Check } from 'lucide-react';
import { Eyebrow } from '../ornament/Eyebrow';

type Ref = { reference: string; gloss: string; verified: boolean };

export function CrossReferenceRail({ references, readingPlan }: { references: Ref[]; readingPlan?: { current: string; next: string } }) {
  if (!references.length && !readingPlan) return null;
  return (
    <aside className="hidden lg:flex flex-col w-[260px] shrink-0 border-l border-rule bg-paper-deep px-5 py-6 overflow-auto">
      {references.length > 0 && (
        <div className="mb-6">
          <Eyebrow className="block mb-3">Cross-references</Eyebrow>
          <div className="space-y-3">
            {references.map((r, i) => (
              <div key={i} className={i > 0 ? 'pt-3 border-t border-rule' : ''}>
                <div className="flex items-center gap-1.5 mb-1">
                  <span className="font-display text-[14px] font-semibold text-ink">{r.reference}</span>
                  {r.verified && <Check size={12} color="#3F6B3A" strokeWidth={2.5} />}
                </div>
                <p className="font-body italic text-[12.5px] text-muted leading-[1.45]">{r.gloss}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      {readingPlan && (
        <div className="bg-card border border-rule rounded-md p-4">
          <Eyebrow className="block mb-2">Reading plan</Eyebrow>
          <p className="font-display text-[14px] font-medium text-ink">{readingPlan.current}</p>
          <p className="font-body italic text-[12px] text-muted mt-1">Next: {readingPlan.next}</p>
        </div>
      )}
    </aside>
  );
}
