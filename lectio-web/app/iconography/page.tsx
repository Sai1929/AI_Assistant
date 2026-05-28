'use client';
import { AppShell } from '@/components/shell/AppShell';
import { SubjectPanel } from '@/components/iconography/SubjectPanel';
import { GalleryPanel } from '@/components/iconography/GalleryPanel';
import { useImageGen } from '@/hooks/useImageGen';

export default function IconographyPage() {
  const { result, isPending, generate, reset } = useImageGen();
  return (
    <AppShell activeTab="iconography">
      <div className="flex h-full overflow-hidden">
        <SubjectPanel onGenerate={generate} isPending={isPending} />
        <GalleryPanel result={result} isPending={isPending} onVariation={reset} />
      </div>
    </AppShell>
  );
}
