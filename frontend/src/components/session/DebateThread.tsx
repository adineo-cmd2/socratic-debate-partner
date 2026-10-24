import { useState } from 'react';
import { apiPost } from '../../lib/apiClient';
import TypingIndicator from './TypingIndicator';

interface Fallacy {
  fallacy_type: string;
  snippet: string;
  confidence: number;
}

interface Item {
  role: 'user' | 'ai';
  content: string;
  fallacies: Fallacy[];
}

export default function DebateThread() {
  const [topic, setTopic] = useState('');
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function start() {
    setError('');
    if (!topic.trim()) {
      setError('Enter a topic to start.');
      return;
    }
    setLoading(true);
    try {
      const data = await apiPost('/api/session/start', { topic: topic.trim() });
      setSessionId(data.session_id as number);
      setItems([]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start session.');
    } finally {
      setLoading(false);
    }
  }

  async function send() {
    setError('');
    if (sessionId == null || !input.trim() || loading) return;
    const message = input.trim();
    setInput('');
    setItems((prev) => [...prev, { role: 'user', content: message, fallacies: [] }]);
    setLoading(true);
    try {
      const data = await apiPost('/api/session/respond', {
        session_id: sessionId,
        message,
      });
      const fallacies = (data.detected_fallacies ?? []) as Fallacy[];
      setItems((prev) => {
        const next = [...prev];
        // Attach detected fallacies to the user message just sent.
        for (let i = next.length - 1; i >= 0; i--) {
          if (next[i].role === 'user' && next[i].content === message) {
            next[i] = { ...next[i], fallacies };
            break;
          }
        }
        next.push({ role: 'ai', content: data.ai_question as string, fallacies: [] });
        return next;
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to send message.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {sessionId == null ? (
        <div className="flex gap-2">
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Debate topic, e.g. Should AI be regulated?"
            className="flex-1 rounded border border-amber bg-transparent px-3 py-2"
          />
          <button
            onClick={() => void start()}
            disabled={loading}
            className="rounded bg-amber px-4 py-2 font-bold text-navy"
          >
            Start
          </button>
        </div>
      ) : (
        <p className="text-sm opacity-80">
          Session #{sessionId} — topic: <span className="serif-q">{topic}</span>{' '}
          <a className="underline" href={`/reasoning-graph?sid=${sessionId}`}>
            view graph
          </a>
        </p>
      )}

      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}

      <div className="mt-4 flex flex-col gap-3">
        {items.map((item, i) =>
          item.role === 'user' ? (
            <div key={i} className="flex justify-end">
              <div className="max-w-[75%] rounded bg-white/10 px-3 py-2">
                <p>{item.content}</p>
                {item.fallacies.length > 0 && (
                  <div className="mt-1">
                    {item.fallacies.map((f, j) => (
                      <span
                        key={j}
                        title={f.snippet}
                        className="mr-1 inline-block rounded border border-amber px-2 py-0.5 text-xs text-amber"
                      >
                        {f.fallacy_type}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div key={i} className="flex justify-start">
              <div className="max-w-[75%] border-l-4 border-amber px-3 py-2">
                <p className="serif-q italic">{item.content}</p>
              </div>
            </div>
          ),
        )}
        {loading && sessionId != null && <TypingIndicator />}
      </div>

      {sessionId != null && (
        <div className="mt-4 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') void send();
            }}
            placeholder="Make your argument…"
            className="flex-1 rounded border border-amber bg-transparent px-3 py-2"
          />
          <button
            onClick={() => void send()}
            disabled={loading}
            className="rounded bg-amber px-4 py-2 font-bold text-navy"
          >
            Send
          </button>
        </div>
      )}
    </div>
  );
}
