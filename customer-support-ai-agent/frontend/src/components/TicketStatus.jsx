export default function TicketStatus({ escalated }) {
  if (!escalated) return null;
  return (
    <div
      style={{
        marginTop: 8,
        padding: "8px 12px",
        borderRadius: 8,
        background: "#2b2410",
        border: "1px solid #6b5a1c",
        fontSize: 13,
      }}
    >
      🎫 This conversation has been escalated to a human support specialist. A ticket has
      been created and someone will follow up shortly.
    </div>
  );
}
