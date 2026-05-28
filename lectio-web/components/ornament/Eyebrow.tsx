export function Eyebrow({ children, className = '', color = 'muted' }: { children: React.ReactNode; className?: string; color?: 'muted' | 'gold' | 'sienna' }) {
  const colors = { muted: 'text-muted', gold: 'text-gold', sienna: 'text-sienna' };
  return <span className={`eyebrow ${colors[color]} ${className}`}>{children}</span>;
}
