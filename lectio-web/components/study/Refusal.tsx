import { Eyebrow } from '../ornament/Eyebrow';

export function Refusal({ message, alternatives = [] }: { message: string; alternatives?: { label: string; action: () => void }[] }) {
  return (
    <div className="py-4">
      <Eyebrow color="sienna" className="block mb-3">A respectful refusal</Eyebrow>
      <div className="pl-5 border-l-2 border-sienna">
        <p className="font-body text-[16px] text-ink leading-[1.7]">{message}</p>
        {alternatives.length > 0 && (
          <div className="flex flex-wrap gap-4 mt-4">
            {alternatives.map((a, i) => (
              <button key={i} onClick={a.action} className="font-ui text-[12px] font-semibold uppercase tracking-[0.15em] text-sienna hover:text-ink transition-colors">
                {a.label} →
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
