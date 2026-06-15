import { useEffect, useState } from "react"
import { api, IndexData } from "../services/api"
import { formatNumber } from "../lib/utils"

export function NEPSEIndexCard() {
  const [data, setData] = useState<IndexData | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    api.index().then((res) => {
      if (res.success && res.data) setData(res.data)
      else setError(res.error || "Failed to load")
    }).catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="card" style={{ color: "var(--destructive)" }}>{error}</div>
  if (!data) return <div className="card">Loading...</div>

  const isUp = data.change >= 0

  return (
    <div className="card">
      <div style={{ fontSize: "0.75rem", color: "var(--muted-foreground)", marginBottom: "0.25rem" }}>
        NEPSE Index
      </div>
      <div style={{ fontSize: "2rem", fontWeight: 700 }}>
        {formatNumber(data.current_value)}
      </div>
      <div style={{ fontSize: "1rem", color: isUp ? "var(--success)" : "var(--destructive)", marginTop: "0.25rem" }}>
        {isUp ? "▲" : "▼"} {isUp ? "+" : ""}{formatNumber(data.change)} ({isUp ? "+" : ""}{formatNumber(data.per_change)}%)
      </div>
      <div style={{ display: "flex", gap: "2rem", marginTop: "1rem", fontSize: "0.8rem", color: "var(--muted-foreground)" }}>
        <div>High: <span style={{ color: "var(--foreground)" }}>{formatNumber(data.high)}</span></div>
        <div>Low: <span style={{ color: "var(--foreground)" }}>{formatNumber(data.low)}</span></div>
      </div>
      <div style={{ display: "flex", gap: "2rem", marginTop: "0.25rem", fontSize: "0.8rem", color: "var(--muted-foreground)" }}>
        <div>52W H: <span style={{ color: "var(--foreground)" }}>{formatNumber(data.fifty_two_week_high)}</span></div>
        <div>52W L: <span style={{ color: "var(--foreground)" }}>{formatNumber(data.fifty_two_week_low)}</span></div>
      </div>
      <div style={{ marginTop: "0.75rem", fontSize: "0.7rem", color: "var(--muted-foreground)" }}>
        {data.generated_time}
      </div>
    </div>
  )
}
