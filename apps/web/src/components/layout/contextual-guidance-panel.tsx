'use client';

import { usePathname } from 'next/navigation';
import { useUiMode } from '@/context/ui-mode-context';

type GuidanceContent = {
  title: string;
  stepMeaning: string;
  nextMove: string;
  mistakes: string[];
};

const DEFAULT_GUIDANCE: GuidanceContent = {
  title: 'AI Guidance',
  stepMeaning: 'This workspace helps you move from idea to integration in small, guided steps.',
  nextMove: 'Pick the next incomplete phase and complete one clear action.',
  mistakes: ['Trying to configure everything at once', 'Skipping validation before integration'],
};

function getGuidance(pathname: string): GuidanceContent {
  if (pathname.includes('/requirements/new')) {
    return {
      title: 'Define',
      stepMeaning: 'Describe what you want to build in plain language. The system turns it into a structured requirement.',
      nextMove: 'Add business goal, users, and data source. Then run Analyze Requirement.',
      mistakes: ['Requirement is too short', 'No success criteria', 'Missing constraints (latency/cost/compliance)'],
    };
  }
  if (pathname.includes('/architecture')) {
    return {
      title: 'Decide',
      stepMeaning: 'Compare architecture choices and select one with confidence.',
      nextMove: 'Start with Recommended, then check trade-offs before confirming.',
      mistakes: ['Choosing only by score', 'Ignoring setup complexity', 'Skipping full-screen graph review'],
    };
  }
  if (pathname.includes('/onboarding')) {
    return {
      title: 'Prepare',
      stepMeaning: 'Complete guided tasks required to make your selected architecture production-ready.',
      nextMove: 'Finish the current task, then validate warnings before moving on.',
      mistakes: ['Skipping required input fields', 'Uploading insufficient data', 'Ignoring validation notices'],
    };
  }
  if (pathname.includes('/studio')) {
    return {
      title: 'Build • Validate • Integrate',
      stepMeaning: 'Build runtime components, test outputs, then generate implementation snippets.',
      nextMove: 'Run build first, test with realistic prompts, then copy integration code.',
      mistakes: ['Testing with toy prompts only', 'Ignoring source/trace signals', 'Integrating before successful build'],
    };
  }
  if (pathname.includes('/projects')) {
    return {
      title: 'Projects',
      stepMeaning: 'Each project tracks one AI system from requirement to integration.',
      nextMove: 'Create a project, then open Define to enter your requirement.',
      mistakes: ['Putting unrelated ideas in one project', 'No project description context'],
    };
  }
  return DEFAULT_GUIDANCE;
}

export function ContextualGuidancePanel() {
  const pathname = usePathname();
  const { isAdvanced } = useUiMode();
  const guidance = getGuidance(pathname);

  return (
    <aside className="hidden w-80 shrink-0 border-l border-zinc-200 bg-white/80 p-4 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/70 xl:block">
      <div className="sticky top-4 space-y-4">
        <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
          <p className="text-xs font-semibold uppercase tracking-wide text-violet-700 dark:text-violet-400">
            {guidance.title}
          </p>
          <div className="mt-3 space-y-3 text-sm">
            <div>
              <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400">What this step means</p>
              <p className="mt-1 text-zinc-700 dark:text-zinc-200">{guidance.stepMeaning}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400">Recommended next move</p>
              <p className="mt-1 text-zinc-700 dark:text-zinc-200">{guidance.nextMove}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-zinc-500 dark:text-zinc-400">Common mistakes</p>
              <ul className="mt-1 list-inside list-disc space-y-1 text-zinc-700 dark:text-zinc-200">
                {guidance.mistakes.map((m) => (
                  <li key={m}>{m}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-md border border-zinc-200 bg-zinc-50 p-2 text-xs text-zinc-600 dark:border-zinc-700 dark:bg-zinc-800/50 dark:text-zinc-300">
              Viewing mode: <span className="font-semibold">{isAdvanced ? 'Advanced' : 'Beginner'}</span>
              {isAdvanced
                ? ' (technical details are expanded where available).'
                : ' (technical details are hidden by default).'}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
