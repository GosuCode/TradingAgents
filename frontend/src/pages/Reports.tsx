import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api, type ReportEntry } from "../services/api"

export function Reports() {
  const [entries, setEntries] = useState<ReportEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.reportsList()
      .then((data) => {
        if (Array.isArray(data)) setEntries(data)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div>Loading...</div>

  if (entries.length === 0) {
    return (
      <div>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Reports</h1>
        <div className="card" style={{ color: "var(--muted-foreground)" }}>
          No reports found. Run an analysis first.
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Reports</h1>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {entries.map((entry) => (
          <div key={`${entry.ticker}-${entry.date}`} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
              <span style={{ fontWeight: 600, fontSize: "1rem" }}>{entry.ticker}</span>
              <span style={{ color: "var(--muted-foreground)", fontSize: "0.8rem" }}>{entry.date}</span>
            </div>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {entry.sections.map((s) => (
                <Link
                  key={s.file}
                  to={`/reports/${entry.ticker}/${entry.date}?section=${s.file.replace(/\.md$/, "")}`}
                  className="card"
                  style={{
                    padding: "0.35rem 0.75rem",
                    fontSize: "0.8rem",
                    textDecoration: "none",
                    color: "var(--foreground)",
                    background: "var(--muted)",
                    borderRadius: "0.375rem",
                  }}
                >
                  {s.name}
                </Link>
              ))}
              <Link
                to={`/reports/${entry.ticker}/${entry.date}`}
                style={{
                  padding: "0.35rem 0.75rem",
                  fontSize: "0.8rem",
                  textDecoration: "none",
                  color: "var(--primary)",
                }}
              >
                View all →
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
