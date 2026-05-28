export function StudyQuestion({ children, time }: { children: string; time: string }) {
  return (
    <div className="border-b border-rule py-4">
      <div className="flex items-baseline gap-2 mb-2">
        <span className="eyebrow text-muted">You asked</span>
        <span className="font-body italic text-[12px] text-muted">{time}</span>
      </div>
      <p className="font-display text-[22px] font-medium text-ink leading-[1.3]">{children}</p>
    </div>
  );
}
