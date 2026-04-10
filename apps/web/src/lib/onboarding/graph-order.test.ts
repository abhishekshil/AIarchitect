import { describe, expect, it } from 'vitest';

import { topologicalOrder } from '@/lib/onboarding/graph-order';

describe('topologicalOrder', () => {
  it('orders dependencies before dependents', () => {
    const ordered = topologicalOrder(
      ['c', 'a', 'b'],
      [
        { source_id: 'a', target_id: 'b', relation: 'depends_on' },
        { source_id: 'b', target_id: 'c', relation: 'depends_on' },
      ],
      ['a', 'b', 'c'],
    );

    expect(ordered).toEqual(['a', 'b', 'c']);
  });

  it('falls back cleanly for cyclic graphs', () => {
    const ordered = topologicalOrder(
      ['a', 'b'],
      [
        { source_id: 'a', target_id: 'b', relation: 'depends_on' },
        { source_id: 'b', target_id: 'a', relation: 'depends_on' },
      ],
      ['b', 'a'],
    );

    expect(ordered).toEqual(['b', 'a']);
  });
});
