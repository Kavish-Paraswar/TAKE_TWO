import { useState, useEffect } from "react";
import Timeline from "./components/Timeline";
import OutputGallery from "./components/OutputGallery";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [runId, setRunId] = useState(null);
  const [token, setToken] = useState(null);
  const [status, setStatus] = useState(null);
  const [messages, setMessages] = useState([]);
  const [outputs, setOutputs] = useState([]);
  const [loadingStart, setLoadingStart] = useState(false);

  async function startRun() {
    if (!title || !description) {
      alert("Please enter title and brief description");
      return;
    }

    setLoadingStart(true);

    const url = `${API}/runs/start?title=${encodeURIComponent(
      title
    )}&description=${encodeURIComponent(description)}`;

    const r = await fetch(url, { method: "POST" });
    if (!r.ok) {
      alert("Failed to start creative run");
      setLoadingStart(false);
      return;
    }

    const data = await r.json();
    setRunId(data.run_id);
    setToken(data.token);
    setLoadingStart(false);
  }

  async function approve() {
    if (!runId || !token) return;

    await fetch(`${API}/runs/${runId}/approve?token=${token}`, {
      method: "POST",
    });

    alert("Creative run approved.");

    resetUI();
  }

  async function interrupt() {
    if (!runId || !token) return;

    await fetch(`${API}/runs/${runId}/interrupt?token=${token}`, {
      method: "POST",
    });

    alert("Creative run interrupted.");

    resetUI();
  }

  function resetUI() {
    setRunId(null);
    setToken(null);
    setStatus(null);
    setMessages([]);
    setOutputs([]);
    setTitle("");
    setDescription("");
  }

  useEffect(() => {
    if (!runId || !token) return;

    const i = setInterval(async () => {
      try {
        const s = await (
          await fetch(`${API}/runs/${runId}/status?token=${token}`)
        ).json();
        setStatus(s);

        const msgs = await (
          await fetch(`${API}/runs/${runId}/agents?token=${token}`)
        ).json();
        setMessages(msgs);

        const outs = await (
          await fetch(`${API}/runs/${runId}/outputs?token=${token}`)
        ).json();
        setOutputs(outs);

        if (
          s.state === "COMPLETED" ||
          s.state === "INTERRUPTED" ||
          s.state === "APPROVED" ||
          s.state === "FAILED"
        ) {
          clearInterval(i);
        }
      } catch (e) {
        console.error(e);
      }
    }, 1000);

    return () => clearInterval(i);
  }, [runId, token]);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(180deg, #0f0f0f, #181818)",
        color: "#e5e7eb",
        padding: 48,
        fontFamily: "Inter, system-ui, sans-serif",
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: 40 }}>
        <h1 style={{ fontSize: 36, marginBottom: 6 }}>Creative Ops Desk</h1>
        <p style={{ opacity: 0.6 }}>
          AI-powered creative execution — you stay the director.
        </p>
      </div>

      {/* Brief Input */}
      {!runId && (
        <div
          style={{
            maxWidth: 640,
            background: "#1b1b1b",
            border: "1px solid #2a2a2a",
            borderRadius: 14,
            padding: 28,
            marginBottom: 48,
          }}
        >
          <h2 style={{ marginBottom: 16 }}>Create Creative Brief</h2>

          <input
            placeholder="Creative title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={inputStyle}
          />

          <textarea
            placeholder="Describe the creative goal, style, tone, constraints…"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            style={{ ...inputStyle, resize: "none" }}
          />

          <button
            onClick={startRun}
            disabled={loadingStart}
            style={{
              marginTop: 12,
              padding: "12px 20px",
              borderRadius: 10,
              background: "#2563eb",
              color: "#fff",
              border: "none",
              cursor: "pointer",
            }}
          >
            {loadingStart ? "Starting…" : "Start Creative Run"}
          </button>
        </div>
      )}

      {/* Control Panel */}
      {runId && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginBottom: 32,
            background: "#161616",
            border: "1px solid #2a2a2a",
            borderRadius: 12,
            padding: "14px 18px",
          }}
        >
          <strong>Status:</strong>
          <span>{status?.state}</span>
          <span style={{ opacity: 0.6 }}>{status?.progress}%</span>

          <button
            style={{
              ...approveBtn,
              opacity: status?.state === "COMPLETED" ? 1 : 0.5,
              cursor: status?.state === "COMPLETED" ? "pointer" : "not-allowed",
            }}
            disabled={status?.state !== "COMPLETED"}
            onClick={approve}
          >
            Approve
          </button>

          <button style={interruptBtn} onClick={interrupt}>
            Interrupt
          </button>
        </div>
      )}

      {/* {runId && (
        <div
          style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40 }}
        >
          <Timeline messages={Array.isArray(messages) ? messages : []} />
          <OutputGallery outputs={Array.isArray(outputs) ? outputs : []} />
        </div>
      )} */}
      {runId && (
        <div>
          <Timeline messages={messages} />
          <OutputGallery outputs={outputs} />
        </div>
      )}
    </div>
  );
}

const inputStyle = {
  width: "100%",
  padding: 12,
  marginBottom: 14,
  borderRadius: 8,
  background: "#111",
  color: "#fff",
  border: "1px solid #333",
  outline: "none",
};

const approveBtn = {
  padding: "8px 14px",
  borderRadius: 8,
  background: "#16a34a",
  border: "none",
  color: "#fff",
  cursor: "pointer",
};

const interruptBtn = {
  padding: "8px 14px",
  borderRadius: 8,
  background: "#7f1d1d",
  border: "none",
  color: "#fff",
  cursor: "pointer",
};
