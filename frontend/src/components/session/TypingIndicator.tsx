export default function TypingIndicator() {
  return (
    <div className="flex justify-start" aria-live="polite" aria-label="AI is thinking">
      <div className="border-l-4 border-amber px-3 py-2">
        <span className="animate-pulse text-amber">● ● ●</span>
      </div>
    </div>
  );
}
