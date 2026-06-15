import { useEffect, useRef, useState } from "react"

interface ProgressMsg {
  type: string
  data?: any
  agent?: string
  percent?: number
  message?: string
}

interface Props {
  messages: ProgressMsg[]
  progress: number
  status: string
}

export function ProgressStream({ messages, progress, status }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const isRunning = status === "running" || status === "queued"

  return (
    <div className="card" style={{ flex: 1, maxHeight: 400, overflowY: "auto", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
        <h3 style={{ margin: 0, fontSize: "0.875rem", fontWeight: 600 }}>Progress</h3>
        {isRunning && (
          <div style={{ width: 200, height: 6, background: "var(--muted)", borderRadius: 3, overflow: "hidden" }}>
            <div style={{ width: `${progress}%`, height: "100%", background: "var(--primary)", transition: "width 0.3s" }} />
          </div>
        )}
      </div>
      <div style={{ fontSize: "0.8rem", fontFamily: "monospace", flex: 1 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ padding: "0.25rem 0", borderBottom: i < messages.length - 1 ? "1px solid var(--border)" : "none" }}>
            {msg.type === "log" && <span style={{ color: "var(--muted-foreground)" }}>→ {msg.data}</span>}
            {msg.type === "agent_start" && <span style={{ color: "var(--primary)" }}>▶ {msg.agent || msg.data}</span>}
            {msg.type === "agent_complete" && <span style={{ color: "var(--success)" }}>✓ {msg.agent || msg.data}</span>}
            {msg.type === "complete" && (
              <span style={{ color: "var(--success)", fontWeight: 700 }}>✅ Complete — {msg.data?.decision || ""}</span>
            )}
            {msg.type === "error" && <span style={{ color: "var(--destructive)" }}>✗ {msg.data}</span>}
          </div>
        ))}
        {isRunning && <div style={{ color: "var(--muted-foreground)" }}>...</div>}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
