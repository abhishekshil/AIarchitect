'use client';

import { useAuth } from '@/context/auth-context';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const primaryLinks = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/projects', label: 'Projects' },
  { href: '/settings', label: 'Settings' },
] as const;

const phaseLinks = [
  { key: 'define', label: 'Define' },
  { key: 'decide', label: 'Decide' },
  { key: 'prepare', label: 'Prepare' },
  { key: 'build', label: 'Build' },
  { key: 'validate', label: 'Validate' },
  { key: 'integrate', label: 'Integrate' },
] as const;

export function MainNav() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const projectMatch = pathname.match(/\/projects\/([^/]+)/);
  const requirementMatch = pathname.match(/\/requirements\/([^/]+)/);
  const currentProjectId = projectMatch?.[1] ?? null;
  const currentRequirementId = requirementMatch?.[1] ?? null;

  return (
    <nav className="flex flex-col gap-1 text-sm">
      {primaryLinks.map(({ href, label }) => {
        const active =
          href === '/projects'
            ? pathname === '/projects' || pathname.startsWith('/projects/')
            : pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link
            key={href}
            href={href}
            className={`rounded-md px-3 py-2 font-medium transition-colors ${
              active
                ? 'bg-zinc-200 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-50'
                : 'text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-900'
            }`}
          >
            {label}
          </Link>
        );
      })}
      {currentProjectId ? (
        <div className="mt-4 rounded-lg border border-zinc-200 bg-zinc-50/80 p-2 dark:border-zinc-800 dark:bg-zinc-900/40">
          <p className="px-2 pb-1 text-[11px] font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            Project journey
          </p>
          <div className="flex flex-col gap-1">
            {phaseLinks.map((phase) => {
              const unavailable = (phase.key === 'decide' || phase.key === 'prepare') && !currentRequirementId;
              const active =
                phase.key === 'define'
                  ? pathname.startsWith(`/projects/${currentProjectId}/requirements/new`)
                  : phase.key === 'decide'
                    ? pathname.includes('/architecture')
                    : phase.key === 'prepare'
                      ? pathname.includes('/onboarding')
                      : phase.key === 'build'
                        ? pathname === `/projects/${currentProjectId}/studio/build`
                        : phase.key === 'validate'
                          ? pathname === `/projects/${currentProjectId}/studio/validate`
                          : pathname === `/projects/${currentProjectId}/studio/integrate`;

              return (
                <span
                  key={phase.key}
                  className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                    active
                      ? 'bg-white text-zinc-900 dark:bg-zinc-800 dark:text-zinc-50'
                      : unavailable
                        ? 'text-zinc-400 dark:text-zinc-600'
                        : 'text-zinc-600 dark:text-zinc-400'
                  }`}
                  aria-disabled="true"
                >
                  {phase.label}
                </span>
              );
            })}
          </div>
        </div>
      ) : null}
      <div className="mt-6 border-t border-zinc-200 pt-4 dark:border-zinc-800">
        <p className="truncate px-3 text-xs text-zinc-500 dark:text-zinc-400" title={user?.email}>
          {user?.email ?? '—'}
        </p>
        <button
          type="button"
          onClick={() => {
            logout();
            window.location.href = '/login';
          }}
          className="mt-2 w-full rounded-md px-3 py-2 text-left text-sm text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/40"
        >
          Sign out
        </button>
      </div>
    </nav>
  );
}
