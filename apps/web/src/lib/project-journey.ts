export type ProjectJourneyEntry = {
  path: string;
  updated_at: string;
};

const STORAGE_KEY = 'aspe-project-journey-v1';
const REQUIREMENT_STORAGE_KEY = 'aspe-requirement-journey-v1';

function readAll(): Record<string, ProjectJourneyEntry> {
  if (typeof window === 'undefined') return {};
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    const out: Record<string, ProjectJourneyEntry> = {};
    for (const [projectId, value] of Object.entries(parsed)) {
      if (!value || typeof value !== 'object') continue;
      const entry = value as Record<string, unknown>;
      const path = typeof entry.path === 'string' ? entry.path : null;
      const updatedAt = typeof entry.updated_at === 'string' ? entry.updated_at : null;
      if (!path || !updatedAt) continue;
      out[projectId] = { path, updated_at: updatedAt };
    }
    return out;
  } catch {
    return {};
  }
}

function writeAll(entries: Record<string, ProjectJourneyEntry>): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

function readRequirementAll(): Record<string, ProjectJourneyEntry> {
  if (typeof window === 'undefined') return {};
  const raw = window.localStorage.getItem(REQUIREMENT_STORAGE_KEY);
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    const out: Record<string, ProjectJourneyEntry> = {};
    for (const [key, value] of Object.entries(parsed)) {
      if (!value || typeof value !== 'object') continue;
      const entry = value as Record<string, unknown>;
      const path = typeof entry.path === 'string' ? entry.path : null;
      const updatedAt = typeof entry.updated_at === 'string' ? entry.updated_at : null;
      if (!path || !updatedAt) continue;
      out[key] = { path, updated_at: updatedAt };
    }
    return out;
  } catch {
    return {};
  }
}

function writeRequirementAll(entries: Record<string, ProjectJourneyEntry>): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(REQUIREMENT_STORAGE_KEY, JSON.stringify(entries));
}

export function saveProjectJourney(projectId: string, path: string): void {
  if (!projectId || !path || typeof window === 'undefined') return;
  const all = readAll();
  all[projectId] = {
    path,
    updated_at: new Date().toISOString(),
  };
  writeAll(all);

  const requirementMatch = path.match(/\/projects\/([^/]+)\/requirements\/([^/]+)/);
  if (requirementMatch) {
    const key = `${requirementMatch[1]}:${requirementMatch[2]}`;
    const requirementAll = readRequirementAll();
    requirementAll[key] = {
      path,
      updated_at: new Date().toISOString(),
    };
    writeRequirementAll(requirementAll);
  }
}

export function getProjectJourney(projectId: string): ProjectJourneyEntry | null {
  const all = readAll();
  return all[projectId] ?? null;
}

export function getRequirementJourney(projectId: string, requirementId: string): ProjectJourneyEntry | null {
  const all = readRequirementAll();
  return all[`${projectId}:${requirementId}`] ?? null;
}

export function clearProjectJourney(projectId: string): void {
  if (!projectId || typeof window === 'undefined') return;
  const all = readAll();
  delete all[projectId];
  writeAll(all);

  const requirementAll = readRequirementAll();
  const prefix = `${projectId}:`;
  for (const key of Object.keys(requirementAll)) {
    if (key.startsWith(prefix)) delete requirementAll[key];
  }
  writeRequirementAll(requirementAll);
}

export function journeyStep(path: string): { step: number; label: string } {
  if (path.includes('/studio/integrate')) return { step: 6, label: 'Integrate' };
  if (path.includes('/studio/validate')) return { step: 5, label: 'Validate' };
  if (path.includes('/studio/build')) return { step: 4, label: 'Build' };
  if (path.includes('/onboarding')) return { step: 3, label: 'Prepare' };
  if (path.includes('/architecture')) return { step: 2, label: 'Decide' };
  return { step: 1, label: 'Define' };
}
