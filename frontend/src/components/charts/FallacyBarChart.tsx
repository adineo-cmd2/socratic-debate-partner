import { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { apiGet } from '../../lib/apiClient';

interface ProfileRow {
  fallacy_type: string;
  count: number;
  examples: string[];
}

export default function FallacyBarChart() {
  const [rows, setRows] = useState<ProfileRow[]>([]);
  const [mounted, setMounted] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setMounted(true);
    apiGet('/api/user/fallacy-profile')
      .then((data) => setRows((data.profile ?? []) as ProfileRow[]))
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : 'Failed to load fallacy profile.'),
      );
  }, []);

  if (!mounted) return <p className="text-sm opacity-70">Loading chart…</p>;
  if (error) return <p className="text-sm text-red-400">{error}</p>;
  if (rows.length === 0)
    return (
      <p className="text-sm opacity-70">
        No fallacies recorded yet — a clean record. Debate more to see your profile.
      </p>
    );

  return (
    <div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows}>
            <XAxis dataKey="fallacy_type" tick={{ fill: '#f5f1e6', fontSize: 12 }} />
            <YAxis tick={{ fill: '#f5f1e6', fontSize: 12 }} allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#d9a441" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <ul className="mt-2 flex flex-col gap-1">
        {rows.map((r) => (
          <li key={r.fallacy_type} className="text-sm">
            <strong>{r.fallacy_type}</strong> × {r.count}
            {r.examples.slice(0, 2).map((ex, i) => (
              <span key={i} className="serif-q block italic opacity-80">
                “{ex}”
              </span>
            ))}
          </li>
        ))}
      </ul>
    </div>
  );
}
