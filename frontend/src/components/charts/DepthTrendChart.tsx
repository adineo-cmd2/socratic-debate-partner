import { useEffect, useState } from 'react';
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { apiGet } from '../../lib/apiClient';

interface Point {
  session: number;
  depth: number;
  fallacies: number;
}

export default function DepthTrendChart() {
  const [points, setPoints] = useState<Point[]>([]);
  const [mounted, setMounted] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setMounted(true);
    apiGet('/api/user/progress')
      .then((data) => {
        const depths = (data.depth_trend ?? []) as number[];
        const falls = (data.fallacy_trend ?? []) as number[];
        setPoints(
          depths.map((d, i) => ({ session: i + 1, depth: d, fallacies: falls[i] ?? 0 })),
        );
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : 'Failed to load progress.'),
      );
  }, []);

  if (!mounted) return <p className="text-sm opacity-70">Loading chart…</p>;
  if (error) return <p className="text-sm text-red-400">{error}</p>;
  if (points.length === 0)
    return (
      <p className="text-sm opacity-70">
        No sessions yet. Your reasoning depth over time will appear here.
      </p>
    );

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points}>
          <XAxis dataKey="session" tick={{ fill: '#f5f1e6', fontSize: 12 }} />
          <YAxis tick={{ fill: '#f5f1e6', fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey="depth" stroke="#d9a441" dot={false} />
          <Line type="monotone" dataKey="fallacies" stroke="#f87171" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
