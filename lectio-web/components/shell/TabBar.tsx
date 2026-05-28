'use client';
import Link from 'next/link';

type Tab = 'study' | 'iconography' | 'evaluation';
const tabs: { value: Tab; label: string; href: string }[] = [
  { value: 'study', label: 'Study', href: '/study' },
  { value: 'iconography', label: 'Iconography', href: '/iconography' },
  { value: 'evaluation', label: 'Evaluation', href: '/evaluation' },
];

export function TabBar({ activeTab }: { activeTab: Tab }) {
  return (
    <div className="flex items-center justify-between px-9 border-b border-rule bg-paper shrink-0">
      <nav className="flex gap-8">
        {tabs.map(t => (
          <Link
            key={t.value}
            href={t.href}
            className={`py-4 text-[11.5px] font-ui font-semibold uppercase tracking-widest transition-colors border-b-[1.5px] ${activeTab === t.value ? 'text-ink border-gold' : 'text-muted border-transparent hover:text-ink-soft'}`}
          >
            {t.label}
          </Link>
        ))}
      </nav>
      <div className="flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-success" />
        <span className="font-body italic text-[12px] text-muted">Connected · KJV · DRA · WEB</span>
      </div>
    </div>
  );
}
