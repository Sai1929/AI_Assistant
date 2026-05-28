'use client';
import { Trash2 } from 'lucide-react';

export function ConfirmModal({ title, body, confirmLabel, onConfirm, onCancel }: {
  title: string; body: string; confirmLabel: string; onConfirm: () => void; onCancel: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-card border border-rule rounded-md shadow-modal w-[420px] p-7">
        <div className="w-11 h-11 rounded-md bg-red-50 flex items-center justify-center mb-5">
          <Trash2 size={20} color="#9B3232" />
        </div>
        <h2 className="font-display text-[22px] font-bold text-ink mb-2">{title}</h2>
        <p className="font-body text-[13.5px] text-muted leading-[1.55] mb-6">{body}</p>
        <div className="flex justify-end gap-3">
          <button onClick={onCancel} className="px-4 py-2 border border-rule rounded-sm text-[11px] font-ui font-semibold uppercase tracking-wide text-ink hover:bg-paper-deep transition-colors">Cancel</button>
          <button onClick={onConfirm} className="px-4 py-2 bg-error text-paper rounded-sm text-[11px] font-ui font-semibold uppercase tracking-wide hover:opacity-90 transition-opacity">{confirmLabel}</button>
        </div>
      </div>
    </div>
  );
}
