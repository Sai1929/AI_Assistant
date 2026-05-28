'use client';
import { useState, useRef, useEffect } from 'react';
import { AppShell } from '@/components/shell/AppShell';
import { Composer } from '@/components/shell/Composer';
import { StudyQuestion } from '@/components/study/StudyQuestion';
import { StudyAnswer } from '@/components/study/StudyAnswer';
import { ScriptureMonument } from '@/components/study/ScriptureMonument';
import { Refusal } from '@/components/study/Refusal';
import { Typing } from '@/components/study/Typing';
import { GeneratedImageBlock } from '@/components/study/GeneratedImageBlock';
import { CrossReferenceRail } from '@/components/study/CrossReferenceRail';
import { Fleuron } from '@/components/ornament/Fleuron';
import { Eyebrow } from '@/components/ornament/Eyebrow';
import { useChat } from '@/hooks/useChat';
import { getLiturgicalHint } from '@/lib/liturgical-calendar';
import type { Intent } from '@/lib/types';

const STARTERS = [
  { cat: 'Scripture', prompt: 'What does John 3:16 mean in context?' },
  { cat: 'Theology', prompt: 'How do the three traditions view Mary?' },
  { cat: 'Practice', prompt: 'A short prayer for difficult times.' },
  { cat: 'Iconography', prompt: 'A symbolic nativity at dusk.' },
];

export default function StudyPage() {
  const { messages, isPending, send } = useChat();
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const hint = getLiturgicalHint();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isPending]);

  function handleSubmit() {
    const v = input.trim();
    if (!v || isPending) return;
    send(v);
    setInput('');
  }

  const lastMsg = messages[messages.length - 1];
  const refs = lastMsg?.meta?.cross_references ?? [];
  const plan = lastMsg?.meta?.reading_plan;

  const composer = <Composer value={input} onChange={setInput} onSubmit={handleSubmit} placeholder={messages.length > 0 ? 'Continue the conversation…' : 'Ask of scripture…'} isSending={isPending} />;

  return (
    <AppShell activeTab="study" composer={composer}>
      <div className="flex h-full overflow-hidden">
        <main className="flex-1 overflow-auto px-14 py-8">
          <div className="mx-auto max-w-[680px]">
            {messages.length === 0 && (
              <div className="flex flex-col items-center gap-8 pt-8">
                <Fleuron width={80} />
                <div className="text-center">
                  <Eyebrow className="block mb-4">An invitation</Eyebrow>
                  <h1 className="font-display text-[56px] font-medium leading-[1.05] text-ink">
                    Ask of scripture,{' '}
                    <span className="italic text-sienna">and let it answer.</span>
                  </h1>
                  <p className="mt-4 font-body text-[15px] text-ink-soft max-w-[460px] mx-auto leading-[1.7]">
                    Every verse is verified against the KJV, Douay-Rheims, and World English Bible. Denomination-aware. Hallucination-resistant.
                  </p>
                </div>
                <div>
                  <Eyebrow className="block text-center mb-4">You might begin with</Eyebrow>
                  <div className="grid grid-cols-2 gap-0 border border-rule rounded-sm overflow-hidden">
                    {STARTERS.map((s, i) => (
                      <button
                        key={i}
                        onClick={() => { setInput(s.prompt); send(s.prompt); }}
                        className={`text-left p-5 hover:bg-paper-deep transition-colors ${i % 2 === 0 ? 'border-r border-rule' : ''} ${i < 2 ? 'border-b border-rule' : ''}`}
                      >
                        <Eyebrow color="gold" className="block mb-2">{s.cat}</Eyebrow>
                        <p className="font-display text-[19px] font-medium text-ink">{s.prompt}</p>
                      </button>
                    ))}
                  </div>
                </div>
                <Fleuron width={60} />
                <p className="font-body italic text-[12.5px] text-muted">⊕ Today: {hint.label}</p>
              </div>
            )}

            {messages.map((m) => {
              if (m.role === 'user') return <StudyQuestion key={m.id} time={m.time}>{m.content}</StudyQuestion>;
              const intent = (m.meta?.intent ?? 'general_chat') as Intent;
              if (intent === 'refuse') return (
                <Refusal key={m.id} message={m.content}
                  alternatives={(m.meta?.alternatives ?? []).map(a => ({ label: a.label, action: () => { setInput(a.prompt); send(a.prompt); } }))}
                />
              );
              if (intent === 'image_gen' && m.meta?.image_b64) return (
                <StudyAnswer key={m.id} intent={intent} time={m.time}>
                  <GeneratedImageBlock
                    src={`data:image/png;base64,${m.meta.image_b64}`}
                    rewrittenPrompt={m.content}
                    onDownload={() => {
                      const a = document.createElement('a'); a.href = `data:image/png;base64,${m.meta!.image_b64}`; a.download = 'lectio.png'; a.click();
                    }}
                    onVariation={() => send(m.content)}
                  />
                </StudyAnswer>
              );
              return (
                <StudyAnswer key={m.id} intent={intent} translation={m.meta?.citations?.[0]?.translation} denomination={m.meta?.denomination ?? undefined} time={m.time}>
                  <p>{m.content}</p>
                  {(m.meta?.citations ?? []).map((c, ci) => (
                    <ScriptureMonument key={ci} verse={c.verse_text ?? m.content} reference={c.reference} translation={c.translation} verified={c.verified} />
                  ))}
                </StudyAnswer>
              );
            })}

            {isPending && <Typing />}
            <div ref={bottomRef} />
          </div>
        </main>
        <CrossReferenceRail references={refs} readingPlan={plan} />
      </div>
    </AppShell>
  );
}
