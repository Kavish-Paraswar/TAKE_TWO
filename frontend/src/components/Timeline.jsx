export default function Timeline({ messages }) {
  if (!messages || messages.length === 0) return null;

  return (
    <div style={{ marginTop: 40 }}>
      <h2 style={{ marginBottom: 16 }}>Agent Activity</h2>

      {messages.map((m) => (
        <div
          key={m.id}
          style={{
            padding: "12px 16px",
            borderLeft: "3px solid #3b82f6",
            marginBottom: 10,
            background: "#1a1a1a",
            borderRadius: 6,
          }}
        >
          <div style={{ fontSize: 13, opacity: 0.6 }}>
            {new Date(m.timestamp).toLocaleTimeString()}
          </div>
          <div style={{ fontWeight: 600 }}>{m.role}</div>
          <div style={{ fontSize: 14 }}>{m.content}</div>
        </div>
      ))}
    </div>
  );
}
