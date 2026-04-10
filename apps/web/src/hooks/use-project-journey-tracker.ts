'use client';

import { saveProjectJourney } from '@/lib/project-journey';
import { usePathname } from 'next/navigation';
import { useEffect } from 'react';

export function useProjectJourneyTracker(projectId: string) {
  const pathname = usePathname();

  useEffect(() => {
    if (!projectId || !pathname) return;
    saveProjectJourney(projectId, pathname);
  }, [projectId, pathname]);
}
