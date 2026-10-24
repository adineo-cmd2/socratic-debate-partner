import { useEffect, useState } from 'react';
import { apiGet } from '../../lib/apiClient';

interface GraphNode {
  id: string | number;
  label: string;
  status: string;
}

interface GraphEdge {
  from: string | number;
  to: string | number;
}

interface Props {
  initialSid?: string;
}

const STATUS_COLOR: Record<string, string> = {
  open: '#d9a441',
  supported: '#4ade80',
  challenged: '#f87171',
};

export default function ReasoningGraph({ initialSid = '' }: Props) {
  const [sid, setSid] = useState(initialSid);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const [ForceGraph, setForceGraph] = useState<any>(null);
  const [error, setError] = useState('');

  // force-graph touches `window` at import time, so load it only in the
  // browser (this island hydrates with client:visible; SSR renders fallback).
  useEffect(() => {
    void import('react-force-graph-2d').then((m) => setForceGraph(() => m.default));
  }, []);

  useEffect(() => {
    if (initialSid) void load(initialSid);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialSid]);

  async function load(id: string) {
    setError('');
    setSelected(null);
    if (!id.trim()) {
      setError('Enter a session id to load its graph.');
      return;
    }
    try {
      const data = await apiGet(`/api/session/${id.trim()}/graph`);
      setNodes((data.nodes ?? []) as GraphNode[]);
      setEdges((data.edges ?? []) as GraphEdge[]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load graph.');
    }
  }

  const graphData = {
    nodes: nodes.map((n) => ({ id: n.id, label: n.label, status: n.status })),
    links: edges.map((e) => ({ source: e.from, target: e.to })),
  };

  return (
    <div>
      <div className="flex gap-2">
        <input
          value={sid}
          onChange={(e) => setSid(e.target.value)}
          placeholder="Session id"
          className="w-40 rounded border border-amber bg-transparent px-3 py-2"
        />
        <button
          onClick={() => void load(sid)}
          className="rounded bg-amber px-4 py-2 font-bold text-navy"
        >
          Load
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}

      {nodes.length === 0 ? (
        <p className="mt-4 text-sm opacity-70">
          No reasoning nodes yet. Start a debate first, then load its graph here.
        </p>
      ) : ForceGraph == null ? (
        <p className="mt-4 text-sm opacity-70">Loading graph…</p>
      ) : (
        <div className="mt-4">
          <ForceGraph
            graphData={graphData}
            nodeLabel="label"
            nodeColor={(n: { status?: string }) =>
              STATUS_COLOR[String(n.status ?? 'open')] ?? '#d9a441'
            }
            onNodeClick={(n: { id: string | number }) => {
              const full = nodes.find((x) => String(x.id) === String(n.id)) ?? null;
              setSelected(full);
            }}
          />
          {selected && (
            <p className="mono-n mt-2 text-sm">
              [{String(selected.status)}] {selected.label}
            </p>
          )}
        </div>
      )}

      {/* List fallback (mobile / no-WebGL): always rendered when nodes exist. */}
      {nodes.length > 0 && (
        <ul className="mt-4 flex flex-col gap-1">
          {nodes.map((n) => (
            <li key={String(n.id)} className="mono-n text-sm">
              [{n.status}] {n.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
