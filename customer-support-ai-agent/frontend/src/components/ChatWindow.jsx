import { useState, useRef, useEffect } from "react";
import Message from "./Message.jsx";
import { sendChatMessage } from "../services/api.js";

const SESSION_ID = "demo-session-" + Math.random().toString(36).slice(2, 8);

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! I'm your support assistant. How can I help today?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || loading) return;
    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);
    try {
      const result = await sendChatMessage(SESSION_ID, null, userMsg.content);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.response,
          sources: result.sources,
          tool_result: result.tool_result,
          escalated: result.escalated,
          confidence: result.confidence,
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
        {messages.map((m, i) => (
          <Message key={i} message={m} />
        ))}
        {loading && <div style={{ opacity: 0.6, fontSize: 13 }}>Assistant is thinking…</div>}
        {error && <div style={{ color: "#e07e7e", fontSize: 13 }}>Error: {error}</div>}
        <div ref={bottomRef} />
      </div>
      <div style={{ display: "flex", padding: 12, borderTop: "1px solid #262a33" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about an order, refund, shipping…"
          style={{
            flex: 1,
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #262a33",
            background: "#0f1115",
            color: "#fff",
          }}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          style={{
            marginLeft: 8,
            padding: "10px 16px",
            borderRadius: 8,
            border: "none",
            background: "#2b5cff",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
