'use client';

import { parseArchitectureGraph, truncateGraphLabel } from '@/components/architecture/architecture-graph-data';
import type { ApiArchitectureRecommendationOption } from '@/types/recommendation';
import { useMemo, useState } from 'react';

type Props = {
  option: ApiArchitectureRecommendationOption;
};

type Point = { x: number; y: number };

export function FullscreenArchitectureGraph({ option }: Props) {
  const { nodes, edges } = parseArchitectureGraph(option);
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState<Point>({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState<Point | null>(null);
  const [activeNodeId, setActiveNodeId] = useState<string | null>(nodes[0]?.id ?? null);

  const incomingCount = useMemo(() => {
    const map = new Map<string, number>();
    nodes.forEach((node) => map.set(node.id, 0));
    edges.forEach((edge) => map.set(edge.target, (map.get(edge.target) ?? 0) + 1));
    return map;
  }, [edges, nodes]);

  const outgoingCount = useMemo(() => {
    const map = new Map<string, number>();
    nodes.forEach((node) => map.set(node.id, 0));
    edges.forEach((edge) => map.set(edge.source, (map.get(edge.source) ?? 0) + 1));
    return map;
  }, [edges, nodes]);

  const activeNode = nodes.find((node) => node.id === activeNodeId) ?? nodes[0] ?? null;
  const incomingFrom = activeNode
    ? edges
        .filter((edge) => edge.target === activeNode.id)
        .map((edge) => nodes.find((node) => node.id === edge.source)?.label ?? edge.source)
    : [];
  const outgoingTo = activeNode
    ? edges
        .filter((edge) => edge.source === activeNode.id)
        .map((edge) => nodes.find((node) => node.id === edge.target)?.label ?? edge.target)
    : [];

  const graph = useMemo(() => {
    const columns = Math.min(5, Math.max(2, Math.ceil(Math.sqrt(nodes.length))));
    const rows = Math.ceil(nodes.length / columns);
    const width = 1400;
    const height = Math.max(700, rows * 220 + 120);
    const leftPadding = 140;
    const rightPadding = 140;
    const topPadding = 80;
    const bottomPadding = 80;
    const usableWidth = width - leftPadding - rightPadding;
    const colStep = columns === 1 ? usableWidth : usableWidth / (columns - 1);
    const rowStep =
      rows === 1 ? height - topPadding - bottomPadding : (height - topPadding - bottomPadding) / (rows - 1);
    const positions = new Map<string, Point>();

    nodes.forEach((node, index) => {
      const row = Math.floor(index / columns);
      const col = index % columns;
      positions.set(node.id, {
        x: leftPadding + col * colStep,
        y: topPadding + row * rowStep,
      });
    });

    return { width, height, positions };
  }, [nodes]);

  function zoomBy(delta: number) {
    setScale((prev) => Math.max(0.5, Math.min(2.2, Number((prev + delta).toFixed(2)))));
  }

  return (
    <div className="rounded-xl border border-zinc-200 bg-white dark:border-zinc-700 dark:bg-zinc-900">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-200 px-4 py-3 dark:border-zinc-700">
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">{option.title}</h2>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">Drag to pan, use zoom controls to inspect nodes.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => zoomBy(-0.1)}
            className="rounded border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-200 dark:hover:bg-zinc-800"
          >
            -
          </button>
          <span className="w-14 text-center text-xs text-zinc-600 dark:text-zinc-300">{Math.round(scale * 100)}%</span>
          <button
            type="button"
            onClick={() => zoomBy(0.1)}
            className="rounded border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-200 dark:hover:bg-zinc-800"
          >
            +
          </button>
          <button
            type="button"
            onClick={() => {
              setScale(1);
              setOffset({ x: 0, y: 0 });
            }}
            className="rounded border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-200 dark:hover:bg-zinc-800"
          >
            Reset
          </button>
        </div>
      </div>

      <div className="grid h-[75vh] gap-0 md:grid-cols-[1fr_320px]">
        <div
          className={`overflow-hidden bg-zinc-50 dark:bg-zinc-950/50 ${dragging ? 'cursor-grabbing' : 'cursor-grab'}`}
          onMouseDown={(e) => {
            setDragging(true);
            setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
          }}
          onMouseMove={(e) => {
            if (!dragging || !dragStart) return;
            setOffset({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
          }}
          onMouseUp={() => {
            setDragging(false);
            setDragStart(null);
          }}
          onMouseLeave={() => {
            setDragging(false);
            setDragStart(null);
          }}
        >
          <svg viewBox={`0 0 ${graph.width} ${graph.height}`} className="h-full w-full">
            <g transform={`translate(${offset.x}, ${offset.y}) scale(${scale})`}>
              <defs>
                <marker
                  id={`arrow-full-${option.candidate_id}`}
                  markerWidth="10"
                  markerHeight="10"
                  refX="9"
                  refY="5"
                  orient="auto"
                  markerUnits="strokeWidth"
                >
                  <path d="M0,0 L10,5 L0,10 z" className="fill-zinc-400 dark:fill-zinc-500" />
                </marker>
              </defs>
              {edges.map((edge, index) => {
                const source = graph.positions.get(edge.source);
                const target = graph.positions.get(edge.target);
                if (!source || !target) return null;
                const highlighted =
                  activeNode && (edge.source === activeNode.id || edge.target === activeNode.id);
                return (
                  <line
                    key={`${edge.source}-${edge.target}-${index}`}
                    x1={source.x + 64}
                    y1={source.y + 32}
                    x2={target.x - 64}
                    y2={target.y + 32}
                    className={highlighted ? 'stroke-emerald-500 dark:stroke-emerald-400' : 'stroke-zinc-400 dark:stroke-zinc-500'}
                    strokeWidth={highlighted ? 2.5 : 2}
                    markerEnd={`url(#arrow-full-${option.candidate_id})`}
                  />
                );
              })}
              {nodes.map((node) => {
                const point = graph.positions.get(node.id);
                if (!point) return null;
                const isActive = activeNode?.id === node.id;
                return (
                  <g key={node.id} className="cursor-pointer" onClick={() => setActiveNodeId(node.id)}>
                    <rect
                      x={point.x - 72}
                      y={point.y}
                      width={144}
                      height={64}
                      rx={12}
                      className={
                        isActive
                          ? 'fill-emerald-50 stroke-emerald-500 dark:fill-emerald-950/40 dark:stroke-emerald-400'
                          : 'fill-white stroke-zinc-300 dark:fill-zinc-900 dark:stroke-zinc-600'
                      }
                    />
                    <text
                      x={point.x}
                      y={point.y + 38}
                      textAnchor="middle"
                      className={isActive ? 'fill-emerald-800 text-[14px] font-semibold dark:fill-emerald-200' : 'fill-zinc-700 text-[14px] font-medium dark:fill-zinc-200'}
                    >
                      {truncateGraphLabel(node.label, 24)}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>
        </div>
        <aside className="border-l border-zinc-200 bg-white p-4 dark:border-zinc-700 dark:bg-zinc-900">
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">Node details</p>
          {activeNode ? (
            <div className="mt-3 space-y-4">
              <div>
                <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">{activeNode.label}</h3>
                <p className="mt-1 font-mono text-xs text-zinc-500 dark:text-zinc-400">{activeNode.id}</p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="rounded-md border border-zinc-200 bg-zinc-50 p-2 dark:border-zinc-700 dark:bg-zinc-800/70">
                  <p className="text-xs text-zinc-500 dark:text-zinc-400">Incoming</p>
                  <p className="font-semibold text-zinc-900 dark:text-zinc-100">{incomingCount.get(activeNode.id) ?? 0}</p>
                </div>
                <div className="rounded-md border border-zinc-200 bg-zinc-50 p-2 dark:border-zinc-700 dark:bg-zinc-800/70">
                  <p className="text-xs text-zinc-500 dark:text-zinc-400">Outgoing</p>
                  <p className="font-semibold text-zinc-900 dark:text-zinc-100">{outgoingCount.get(activeNode.id) ?? 0}</p>
                </div>
              </div>
              <div>
                <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Receives from</p>
                {incomingFrom.length > 0 ? (
                  <ul className="mt-1 list-inside list-disc text-sm text-zinc-700 dark:text-zinc-200">
                    {incomingFrom.map((label, index) => (
                      <li key={`${label}-${index}`}>{label}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">No inbound dependency.</p>
                )}
              </div>
              <div>
                <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Sends to</p>
                {outgoingTo.length > 0 ? (
                  <ul className="mt-1 list-inside list-disc text-sm text-zinc-700 dark:text-zinc-200">
                    {outgoingTo.map((label, index) => (
                      <li key={`${label}-${index}`}>{label}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Terminal output node.</p>
                )}
              </div>
            </div>
          ) : (
            <p className="mt-3 text-sm text-zinc-500 dark:text-zinc-400">Click any node to inspect details.</p>
          )}
        </aside>
      </div>
    </div>
  );
}
