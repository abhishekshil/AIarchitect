'use client';

import { useAuth } from '@/context/auth-context';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import type { ReactNode } from 'react';

/**
 * Client gate for authenticated segments. Middleware can be added later
 * (e.g. httpOnly session cookie) for SSR-safe redirects.
 */
export function AuthGuard({ children }: { children: ReactNode }) {
  const { token, bootstrapping } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (bootstrapping) return;
    if (!token) router.replace('/login');
  }, [bootstrapping, token, router]);

  if (bootstrapping) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <p className="text-sm text-zinc-500">Loading session…</p>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-8 bg-zinc-50 dark:bg-zinc-950">
        <p className="text-sm text-zinc-600 dark:text-zinc-400">Redirecting to sign in…</p>
        <Link href="/login" className="text-sm text-emerald-700 dark:text-emerald-400 underline">
          Go to login
        </Link>
      </div>
    );
  }

  return <>{children}</>;
}
