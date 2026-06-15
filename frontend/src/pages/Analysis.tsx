import { useState, useCallback, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { api } from "../services/api"
import { connectAnalysisWS } from "../services/websocket"
import { AnalysisForm } from "../components/AnalysisForm"
import { ProgressStream } from "../components/ProgressStream"
import { ReportViewer } from "../components/ReportViewer"

export function Analysis() {
  const navigate = useNavigate()
  const [taskId, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState("")
  const [progress, setProgress] = useState(0)
  const [messages, setMessages] = useState<any[]>([])
  const [result, setResult] = useState<any>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const handleStart = useCallback(async (data: { ticker: string; date: string; vendor: string; llm_provider: string }) => {
    setMessages([])
    setResult(null)
    setProgress(0)

    const res = await api.startAnalysis({
      ticker: data.ticker,
      date: data.date,
      vendor: data.vendor,
      llm_provider: data.llm_provider,
    })
    setTaskId(res.task_id)
    setStatus("queued")
    setMessages([{ type: "log", data: `Task created: ${res.task_id.slice(0, 8)}...` }])

    const ws = connectAnalysisWS(res.task_id, (msg) => {
      setMessages((prev) => [...prev, msg])
      if (msg.type === "progress") {
        setProgress(msg.percent || 0)
      }
      if (msg.type === "log") {
        setStatus("running")
        setProgress((p) => Math.max(p, 10))
      }
      if (msg.type === "complete") {
        setStatus("completed")
        setProgress(100)
        setResult(msg.data)
      }
      if (msg.type === "error") {
        setStatus("failed")
        setMessages((prev) => [...prev, { type: "error", data: msg.data }])
      }
    })
    wsRef.current = ws
  }, [])

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Analysis</h1>
      <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
        <AnalysisForm onStart={handleStart} disabled={status === "running" || status === "queued"} />
        {messages.length > 0 && (
          <div style={{ flex: 1, minWidth: 300 }}>
            <ProgressStream messages={messages} progress={progress} status={status} />
          </div>
        )}
      </div>
      {result && (
        <div style={{ marginTop: "1.5rem" }}>
          <ReportViewer
            decision={result.decision}
            rating={result.rating}
            summary={result.summary}
            ticker={result.ticker}
            date={result.date}
          />
        </div>
      )}
    </div>
  )
}
