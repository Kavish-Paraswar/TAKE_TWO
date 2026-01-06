export default function OutputGallery({ outputs }) {

  if (!Array.isArray(outputs) || outputs.length === 0) {
    return <div style={{ opacity: 0.6 }}>No outputs yet.</div>;
  }

  const byTask = {};
  for (const o of outputs) {
    if (!o || typeof o !== "object") continue;

    const meta = o.meta && typeof o.meta === "object" ? o.meta : {};
    const task = meta.task || "Unknown task";

    if (!byTask[task]) byTask[task] = [];
    byTask[task].push(o);
  }

  const taskEntries = Object.entries(byTask);
  if (taskEntries.length === 0) {
    return <div style={{ opacity: 0.6 }}>No valid outputs yet.</div>;
  }

  return (
    <div style={{ marginTop: 40 }}>
      <h2 style={{ marginBottom: 20 }}>Creative Outputs</h2>

      {taskEntries.map(([task, items]) => {
        if (!Array.isArray(items) || items.length === 0) return null;
        const sorted = [...items].sort((a, b) => {
          const aScore = typeof a?.meta?.score === "number" ? a.meta.score : -1;
          const bScore = typeof b?.meta?.score === "number" ? b.meta.score : -1;
          return bScore - aScore;
        });

        const best = sorted[0];
        if (!best || !best.asset_url) return null;

        const rest = sorted.slice(1);
        const score =
          typeof best.meta?.score === "number" ? best.meta.score : "N/A";

        return (
          <div
            key={task}
            style={{
              marginBottom: 40,
              padding: 20,
              borderRadius: 12,
              background: "#1f1f1f",
              border: "1px solid #333",
            }}
          >
            <h3 style={{ marginBottom: 14 }}>{task}</h3>

            {/* Best Output Row */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 32,
              }}
            >
              {/* Image */}
              <img
                src={best.asset_url}
                alt=""
                style={{
                  width: 280,
                  borderRadius: 10,
                  border: "3px solid #4ade80",
                }}
              />

              {/* Right-side decision panel */}
              <div
                style={{
                  minWidth: 160,
                  textAlign: "right",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "flex-end",
                  gap: 6,
                }}
              >
                <div style={{ fontSize: 14, fontWeight: 600 }}>Best Pick</div>

                <div style={{ fontSize: 12, opacity: 0.6 }}>Critic Score</div>

                <span
                  style={{
                    padding: "6px 14px",
                    borderRadius: 999,
                    fontWeight: 600,
                    fontSize: 13,
                    color: "#000",
                    background:
                      score === "N/A"
                        ? "#9ca3af"
                        : score >= 7
                        ? "#22c55e"
                        : "#facc15",
                  }}
                >
                  {score}
                </span>
              </div>
            </div>

            {/* Other Variants */}
            {rest.length > 0 && (
              <div style={{ marginTop: 18 }}>
                <div
                  style={{
                    fontSize: 13,
                    opacity: 0.7,
                    marginBottom: 8,
                  }}
                >
                  Other Variants
                </div>

                <div style={{ display: "flex", gap: 12 }}>
                  {rest.map((o) =>
                    o && o.asset_url ? (
                      <img
                        key={o.id}
                        src={o.asset_url}
                        alt=""
                        style={{
                          width: 120,
                          borderRadius: 8,
                          opacity: 0.6,
                        }}
                      />
                    ) : null
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
