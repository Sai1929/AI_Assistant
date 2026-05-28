export function Cross({ size = 16, strokeWidth = 2, color = 'currentColor', className = '' }: { size?: number; strokeWidth?: number; color?: string; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M12 3v18" /><path d="M6 9h12" />
    </svg>
  );
}
