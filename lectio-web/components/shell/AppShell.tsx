'use client';
import { Sidebar } from './Sidebar';
import { TabBar } from './TabBar';
import { ConnectionErrorBanner } from '../overlays/ConnectionErrorBanner';
import { useApp } from '@/lib/store';

type Tab = 'study' | 'iconography' | 'evaluation';

export function AppShell({ activeTab, children, composer }: { activeTab: Tab; children: React.ReactNode; composer?: React.ReactNode }) {
  const apiDown = useApp(s => s.apiDown);
  return (
    <div className="flex h-screen overflow-hidden bg-paper">
      <Sidebar />
      <div className="flex flex-1 flex-col min-w-0">
        <TabBar activeTab={activeTab} />
        {apiDown && <ConnectionErrorBanner />}
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-auto">{children}</div>
          {composer && <div className="border-t border-rule bg-paper px-14 py-4">{composer}</div>}
        </div>
      </div>
    </div>
  );
}
