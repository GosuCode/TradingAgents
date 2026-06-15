import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

export function Reports() {
  const [reports, setReports] = useState<any[]>([])

  useEffect(() => {
    fetch("/api/reports")
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data)) setReports(data)
      })
      .catch(() => {})
  }, [])

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Reports</h1>
      {reports.length === 0 ? (
        <div className="card" style={{ color: "var(--muted-foreground)" }}>
          No reports yet. Run an analysis first.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {reports.map((r: any) => (
            <Link
              key={r.task_id}
              to={`/analysis/${r.task_id}`}
              className="card"
              style={{ display: "flex", justifyContent: "space-between", textDecoration: "none", color: "inherit" }}
            >
              <span style={{ fontWeight: 500 }}>{r.ticker}</span>
              <span style={{ color: "var(--muted-foreground)", fontSize: "0.8rem" }}>{r.date}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
