'use client';

import { useScreenUiMode } from '@/context/ui-mode-context';

type Props = {
  screenKey: string;
};

export function ScreenViewToggle({ screenKey }: Props) {
  const { localMode, effectiveMode, setLocalMode } = useScreenUiMode(screenKey);

  return (
    <div className="flex items-center gap-2 rounded-md border border-zinc-200 bg-white px-2 py-1 dark:border-zinc-700 dark:bg-zinc-900">
      <button
        type="button"
        onClick={() => setLocalMode('beginner')}
        className={`rounded px-2 py-1 text-xs font-medium ${
          effectiveMode === 'beginner'
            ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
            : 'text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800'
        }`}
      >
        Simple
      </button>
      <button
        type="button"
        onClick={() => setLocalMode('advanced')}
        className={`rounded px-2 py-1 text-xs font-medium ${
          effectiveMode === 'advanced'
            ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
            : 'text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800'
        }`}
      >
        Technical
      </button>
      <button
        type="button"
        onClick={() => setLocalMode('global')}
        className={`rounded px-2 py-1 text-[11px] ${
          localMode === undefined
            ? 'text-emerald-700 dark:text-emerald-400'
            : 'text-zinc-500 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800'
        }`}
      >
        {localMode === undefined ? 'Using global' : 'Use global'}
      </button>
    </div>
  );
}
