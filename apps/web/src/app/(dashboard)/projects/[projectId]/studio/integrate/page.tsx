import { StudioPageClient } from '@/components/studio/studio-page-client';
import { Suspense } from 'react';

export default function StudioIntegratePage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-5xl space-y-4 p-4">
          <div className="h-10 w-48 animate-pulse rounded bg-zinc-200 dark:bg-zinc-800" />
          <div className="h-64 animate-pulse rounded-xl bg-zinc-200 dark:bg-zinc-800" />
        </div>
      }
    >
      <StudioPageClient section="integrate" />
    </Suspense>
  );
}
