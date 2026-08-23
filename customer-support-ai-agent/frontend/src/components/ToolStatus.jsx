export default function ToolStatus({ toolResult }) {
  if (!toolResult) return null;
  const ok = toolResult.success !== false && toolResult.found !== false;
  return (
    <div
      style={{
        marginTop: 6,
        fontSize: 12,
        padding: "4px 8px",
        borderRadius: 6,
        display: "inline-block",
        background: ok ? "#1b3a2b" : "#3a1b1b",
        color: ok ? "#7ee0a3" : "#e07e7e",
      }}
    >
      {ok ? "✓ Action completed" : `✗ ${toolResult.error || "Action failed"}`}
    </div>
  );
}
