import SourceCitation from "./SourceCitation.jsx";
import ToolStatus from "./ToolStatus.jsx";
import TicketStatus from "./TicketStatus.jsx";

export default function Message({ message }) {
  const isUser = message.role === "user";
  return (
    <div style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", margin: "8px 0" }}>
      <div
        style={{
          maxWidth: "70%",
          background: isUser ? "#2b5cff" : "#1b1e26",
          color: "#fff",
          padding: "10px 14px",
          borderRadius: 12,
        }}
      >
        <div>{message.content}</div>
        {!isUser && <SourceCitation sources={message.sources} />}
        {!isUser && <ToolStatus toolResult={message.tool_result} />}
        {!isUser && <TicketStatus escalated={message.escalated} />}
        {!isUser && message.confidence != null && (
          <div style={{ marginTop: 4, fontSize: 11, opacity: 0.6 }}>
            confidence: {(message.confidence * 100).toFixed(0)}%
          </div>
        )}
      </div>
    </div>
  );
}
