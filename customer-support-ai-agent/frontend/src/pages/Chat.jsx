import ChatWindow from "../components/ChatWindow.jsx";

export default function Chat() {
  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <header style={{ padding: 16, borderBottom: "1px solid #262a33" }}>
        <h2 style={{ margin: 0 }}>Support Assistant</h2>
      </header>
      <div style={{ flex: 1, minHeight: 0 }}>
        <ChatWindow />
      </div>
    </div>
  );
}
