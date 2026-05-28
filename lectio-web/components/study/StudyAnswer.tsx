import { Eyebrow } from '../ornament/Eyebrow';
import type { Intent } from '@/lib/types';

const intentLabels: Record<Intent, string> = {
  scripture_qa: 'Reflection · scripture qa',
  theology: 'Reflection · theology',
  image_gen: 'Iconography · symbolic',
  contradiction: 'Reflection · contradiction',
  general_chat: 'Reflection · general',
  refuse: 'A respectful refusal',
};

export function StudyAnswer({ intent, translation, denomination, time, children }: {
  intent: Intent; translation?: string; denomination?: string; time: string; children: React.ReactNode;
}) {
  const isRefusal = intent === 'refuse';
  return (
    <div className="py-6">
      <div className="flex items-center gap-3 mb-3">
        <Eyebrow color={isRefusal ? 'sienna' : 'gold'}>{intentLabels[intent]}</Eyebrow>
        {translation && <span className="font-mono text-[10.5px] text-muted border border-rule rounded-hairline px-1.5 py-0.5">{translation}</span>}
        {denomination && <span className="font-body italic text-[12px] text-muted">· {denomination} reading</span>}
        <span className="ml-auto font-body italic text-[12px] text-muted">{time}</span>
      </div>
      <div className="font-body text-[15.5px] text-ink-soft leading-[1.7] space-y-4">{children}</div>
    </div>
  );
}
