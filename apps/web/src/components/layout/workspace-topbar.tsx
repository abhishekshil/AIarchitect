'use client';

import { useAuth } from '@/context/auth-context';
import { useUiMode } from '@/context/ui-mode-context';

export function WorkspaceTopbar() {
  const { user } = useAuth();
  const { mode, setMode, isAdvanced } = useUiMode();

  return (
    <header className="border-b border-zinc-200 bg-white/90 px-4 py-3 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/80 md:px-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          <span className="rounded-full bg-zinc-100 p-2 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
            <span className="block h-3 w-3 rounded-full bg-current" />
          </span>
          <span className="truncate text-sm text-zinc-700 dark:text-zinc-200">
            {user?.email ?? 'Workspace'}
          </span>
        </div>
        <button
          type="button"
          onClick={() => setMode(isAdvanced ? 'beginner' : 'advanced')}
          className={`rounded-md border px-3 py-1.5 text-xs font-medium ${
            isAdvanced
              ? 'border-violet-300 bg-violet-50 text-violet-800 dark:border-violet-700 dark:bg-violet-950/40 dark:text-violet-300'
              : 'border-zinc-300 text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900'
          }`}
        >
          {mode === 'advanced' ? 'Advanced mode: On' : 'Advanced mode: Off'}
        </button>
      </div>
    </header>
  );
}
