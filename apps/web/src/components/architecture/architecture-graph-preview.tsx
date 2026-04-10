import type { ApiArchitectureRecommendationOption } from '@/types/recommendation';
import { parseArchitectureGraph, truncateGraphLabel } from '@/components/architecture/architecture-graph-data';

type Props = {
  option: ApiArchitectureRecommendationOption;
};

const MAX_GRAPH_NODES = 10;

export function ArchitectureGraphPreview({ option }: Props) {
  const { nodes, edges } = parseArchitectureGraph(option, MAX_GRAPH_NODES);
  const width = 680;
  const columns = Math.min(4, Math.max(2, Math.ceil(Math.sqrt(nodes.length))));
  const rowHeight = 90;
  const rows = Math.ceil(nodes.length / columns);
  const height = Math.max(170, rows * rowHeight + 30);
  const leftPadding = 80;
  const rightPadding = 60;
  const topPadding = 26;
  const bottomPadding = 26;
  const usableWidth = width - leftPadding - rightPadding;
  const colStep = columns === 1 ? usableWidth : usableWidth / (columns - 1);
  const rowStep = rows === 1 ? height - topPadding - bottomPadding : (height - topPadding - bottomPadding) / (rows - 1);
  const positions = new Map<string, { x: number; y: number }>();

  nodes.forEach((node, index) => {
    const row = Math.floor(index / columns);
    const col = index % columns;
    positions.set(node.id, {
      x: leftPadding + col * colStep,
      y: topPadding + row * rowStep,
    });
  });

  return (
    <div className="overflow-hidden rounded-lg border border-zinc-200 bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-950/40">
      <div className="border-b border-zinc-200 px-3 py-2 text-xs font-medium text-zinc-600 dark:border-zinc-700 dark:text-zinc-300">
        Visual architecture flow
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="h-52 w-full" role="img" aria-label="Architecture graph preview">
        <defs>
          <marker
            id={`arrow-${option.candidate_id}`}
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="4"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L8,4 L0,8 z" className="fill-zinc-400 dark:fill-zinc-500" />
          </marker>
        </defs>
        {edges.map((edge, index) => {
          const source = positions.get(edge.source);
          const target = positions.get(edge.target);
          if (!source || !target) return null;
          return (
            <line
              key={`${edge.source}-${edge.target}-${index}`}
              x1={source.x + 38}
              y1={source.y + 20}
              x2={target.x - 38}
              y2={target.y + 20}
              className="stroke-zinc-400 dark:stroke-zinc-500"
              strokeWidth="1.5"
              markerEnd={`url(#arrow-${option.candidate_id})`}
            />
          );
        })}
        {nodes.map((node) => {
          const point = positions.get(node.id);
          if (!point) return null;
          return (
            <g key={node.id}>
              <rect
                x={point.x - 40}
                y={point.y}
                width={80}
                height={40}
                rx={10}
                className="fill-white stroke-zinc-300 dark:fill-zinc-900 dark:stroke-zinc-600"
              />
              <text
                x={point.x}
                y={point.y + 24}
                textAnchor="middle"
                className="fill-zinc-700 text-[10px] font-medium dark:fill-zinc-200"
              >
                {truncateGraphLabel(node.label)}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
