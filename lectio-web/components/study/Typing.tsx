'use client';
import { useEffect, useState } from 'react';

const CAPTIONS = ['Searching scripture…', 'Considering tradition…', 'Verifying citations…'];

export function Typing() {
  const [caption, setCaption] = useState(0);
  const [showCycle, setShowCycle] = useState(false);

  useEffect(() => {
    const delay = setTimeout(() => setShowCycle(true), 3000);
    return () => clearTimeout(delay);
  }, []);

  useEffect(() => {
    if (!showCycle) return;
    const interval = setInterval(() => setCaption(c => (c + 1) % CAPTIONS.length), 2000);
    return () => clearInterval(interval);
  }, [showCycle]);

  return (
    <div className="flex items-center gap-2 py-4">
      {[0, 1, 2].map(i => (
        <span key={i} className="h-1.5 w-1.5 rounded-full bg-muted" style={{ animation: `dotPulse 1.2s ${i * 0.15}s infinite ease-in-out` }} />
      ))}
      <span className="ml-2 font-body italic text-xs text-muted">{CAPTIONS[caption]}</span>
    </div>
  );
}
