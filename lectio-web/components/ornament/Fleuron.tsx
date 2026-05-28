export function Fleuron({ width = 120 }: { width?: number }) {
  return (
    <div className="mx-auto flex items-center justify-center gap-2.5 text-gold/70" style={{ width }}>
      <span className="h-px flex-1 bg-current opacity-50" />
      <span className="text-[11px] tracking-[4px]">✦</span>
      <span className="h-px flex-1 bg-current opacity-50" />
    </div>
  );
}
