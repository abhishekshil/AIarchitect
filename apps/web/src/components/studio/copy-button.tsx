'use client';

import { copyToClipboard } from '@/lib/clipboard';
import { useState } from 'react';

type Props = {
  text: string;
  label?: string;
  className?: string;
};

export function CopyButton({ text, label = 'Copy', className = '' }: Props) {
  const [done, setDone] = useState(false);

  async function onClick() {
    const ok = await copyToClipboard(text);
    if (ok) {
      setDone(true);
      setTimeout(() => setDone(false), 2000);
    }
  }

  return (
    <button
      type="button"
      onClick={() => void onClick()}
      className={`rounded-md border border-zinc-300 bg-white px-3 py-1.5 text-xs font-medium text-zinc-800 hover:bg-zinc-50 dark:border-zinc-600 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800 ${className}`}
    >
      {done ? 'Copied!' : label}
    </button>
  );
}
