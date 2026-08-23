export default function SourceCitation({ sources }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div style={{ marginTop: 6, fontSize: 12, opacity: 0.75 }}>
      Sources:{" "}
      {sources.map((s, i) => (
        <span key={s.title} style={{ marginRight: 8 }}>
          📄 {s.title}
          {i < sources.length - 1 ? "," : ""}
        </span>
      ))}
    </div>
  );
}
