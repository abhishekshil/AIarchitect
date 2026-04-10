import { MainNav } from '@/components/layout/main-nav';
import Link from 'next/link';
import type { ReactNode } from 'react';

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen flex bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
      <aside className="hidden w-56 shrink-0 flex-col border-r border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950 md:flex">
        <div className="mb-6 px-3">
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
            Planning
          </p>
          <p className="mt-1 text-sm font-semibold text-zinc-900 dark:text-zinc-50">Workspace</p>
        </div>
        <MainNav />
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex flex-wrap items-center gap-3 border-b border-zinc-200 bg-white px-4 py-3 dark:border-zinc-800 dark:bg-zinc-950 md:hidden">
          <Link
            href="/dashboard"
            className="text-sm font-medium text-emerald-800 dark:text-emerald-400"
          >
            Dashboard
          </Link>
          <Link
            href="/projects"
            className="text-sm font-medium text-zinc-700 dark:text-zinc-300"
          >
            Projects
          </Link>
        </header>
        <main className="flex-1 p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}
