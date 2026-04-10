import { describe, expect, it } from 'vitest';

import { isTaskUnlocked } from '@/lib/onboarding/task-unlock';
import type { OnboardingTaskItem } from '@/types/onboarding';

function task(node_id: string, state: OnboardingTaskItem['state']): OnboardingTaskItem {
  return {
    node_id,
    title: node_id,
    description: null,
    task_type: null,
    metadata: null,
    guidance_refs: [],
    condition: null,
    state,
    suggestions: [],
    example_placeholder: '',
    response: null,
    validation_feedback: null,
    updated_at: null,
  };
}

describe('isTaskUnlocked', () => {
  it('enforces linear mode order', () => {
    const t1 = task('one', 'completed');
    const t2 = task('two', 'not_started');
    const t3 = task('three', 'not_started');
    const byId = new Map([
      [t1.node_id, t1],
      [t2.node_id, t2],
      [t3.node_id, t3],
    ]);

    expect(isTaskUnlocked(t2, byId, [], ['one', 'two', 'three'], 'linear')).toBe(true);
    expect(isTaskUnlocked(t3, byId, [], ['one', 'two', 'three'], 'linear')).toBe(false);
  });

  it('enforces graph dependencies in graph mode', () => {
    const parent = task('parent', 'completed');
    const child = task('child', 'not_started');
    const byId = new Map([
      [parent.node_id, parent],
      [child.node_id, child],
    ]);

    const unlocked = isTaskUnlocked(
      child,
      byId,
      [{ source_id: 'parent', target_id: 'child', relation: 'depends_on' }],
      ['parent', 'child'],
      'graph',
    );
    expect(unlocked).toBe(true);
  });
});
