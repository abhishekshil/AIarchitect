'use client';

import { useAuth } from '@/context/auth-context';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const links = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/projects', label: 'Projects' },
] as const;

export function MainNav() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <nav className="flex flex-col gap-1 text-sm">
      {links.map(({ href, label }) => {
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
