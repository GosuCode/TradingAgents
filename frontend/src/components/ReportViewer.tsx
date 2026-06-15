interface Props {
  decision: string
  rating: string
  summary: string
  ticker: string
  date: string
}

export function ReportViewer({ decision, rating, summary, ticker, date }: Props) {
  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h2 style={{ margin: 0, fontSize: "1.1rem" }}>{ticker} — {date}</h2>
        <span style={{
          padding: "0.25rem 0.75rem",
          borderRadius: "1rem",
          fontSize: "0.875rem",
          fontWeight: 600,
          background: rating.toLowerCase().includes("buy") || rating.toLowerCase().includes("overweight")
            ? "rgba(34,197,94,0.15)" : rating.toLowerCase().includes("sell") || rating.toLowerCase().includes("underweight")
            ? "rgba(239,68,68,0.15)" : "rgba(148,163,184,0.15)",
          color: rating.toLowerCase().includes("buy") || rating.toLowerCase().includes("overweight")
            ? "var(--success)" : rating.toLowerCase().includes("sell") || rating.toLowerCase().includes("underweight")
            ? "var(--destructive)" : "var(--muted-foreground)",
        }}>
          {decision}
        </span>
      </div>
      {rating && (
        <div style={{ marginBottom: "0.75rem" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--muted-foreground)" }}>Rating: </span>
          <span style={{ fontWeight: 600 }}>{rating}</span>
        </div>
      )}
      {summary && (
        <div>
          <div style={{ fontSize: "0.75rem", color: "var(--muted-foreground)", marginBottom: "0.25rem" }}>Executive Summary</div>
          <p style={{ margin: 0, fontSize: "0.875rem", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{summary}</p>
        </div>
      )}
    </div>
  )
}
