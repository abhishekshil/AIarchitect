import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-8 p-8 bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
      <div className="max-w-lg text-center space-y-3">
        <p className="text-xs font-medium uppercase tracking-wide text-emerald-700 dark:text-emerald-400">
          AI Solution Planning Engine
        </p>
        <h1 className="text-3xl font-semibold tracking-tight">Plan and ship AI architectures</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-300 leading-relaxed">
          Sign in to open your workspace: dashboard, projects, and upcoming requirement and runtime
          workflows.
        </p>
      </div>
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Link
          href="/login"
          className="rounded-md bg-emerald-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-emerald-800 dark:bg-emerald-600 dark:hover:bg-emerald-500"
        >
          Sign in
        </Link>
        <Link
          href="/register"
          className="rounded-md border border-zinc-300 bg-white px-5 py-2.5 text-sm font-medium text-zinc-800 hover:bg-zinc-50 dark:border-zinc-600 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800"
        >
          Register
        </Link>
        <Link
          href="/dashboard"
          className="rounded-md px-5 py-2.5 text-sm font-medium text-zinc-600 underline dark:text-zinc-400"
        >
          Dashboard
        </Link>
      </div>
      <p className="max-w-md text-center text-xs text-zinc-500 dark:text-zinc-500">
        Configure <code className="rounded bg-zinc-200/80 px-1 py-0.5 dark:bg-zinc-800">NEXT_PUBLIC_API_URL</code>{' '}
        to match your FastAPI server (default <code className="rounded bg-zinc-200/80 px-1 py-0.5 dark:bg-zinc-800">http://127.0.0.1:8000</code>
        ).
      </p>
    </main>
  );
}
