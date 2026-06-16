import { useEffect, useState } from "react"
import { useParams, useSearchParams, Link } from "react-router-dom"
import { api, type ReportDetail as ReportDetailData } from "../services/api"

export function ReportDetail() {
  const { ticker, date } = useParams<{ ticker: string; date: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const [report, setReport] = useState<ReportDetailData | null>(null)
  const [error, setError] = useState("")

  const activeSection = searchParams.get("section") || ""

  useEffect(() => {
    if (!ticker || !date) return
    api.reportDetail(ticker, date)
      .then(setReport)
      .catch((e) => setError(e.message))
  }, [ticker, date])

  if (error) return <div style={{ color: "var(--destructive)" }}>{error}</div>
  if (!report) return <div>Loading...</div>

  const selectedSection = activeSection
    ? report.sections.find((s) => s.file.replace(/\.md$/, "") === activeSection)
    : null

  return (
    <div>
      <div style={{ marginBottom: "1.5rem" }}>
        <Link to="/reports" style={{ color: "var(--muted-foreground)", fontSize: "0.8rem", textDecoration: "none" }}>
          ← Back to Reports
        </Link>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: "0.25rem 0 0" }}>
          {ticker} — {date}
        </h1>
      </div>

      {report.sections.length > 1 && (
        <div style={{ display: "flex", gap: "0.25rem", marginBottom: "1rem", flexWrap: "wrap" }}>
          <button
            onClick={() => setSearchParams({})}
            style={{
              padding: "0.35rem 0.75rem",
              border: "1px solid var(--border)",
              borderRadius: "0.375rem",
              background: !activeSection ? "var(--primary)" : "var(--card)",
              color: !activeSection ? "white" : "var(--foreground)",
              cursor: "pointer",
              fontSize: "0.8rem",
            }}
          >
            All
          </button>
          {report.sections.map((s) => {
            const key = s.file.replace(/\.md$/, "")
            return (
              <button
                key={key}
                onClick={() => setSearchParams({ section: key })}
                style={{
                  padding: "0.35rem 0.75rem",
                  border: "1px solid var(--border)",
                  borderRadius: "0.375rem",
                  background: activeSection === key ? "var(--primary)" : "var(--card)",
                  color: activeSection === key ? "white" : "var(--foreground)",
                  cursor: "pointer",
                  fontSize: "0.8rem",
                }}
              >
                {s.name}
              </button>
            )
          })}
        </div>
      )}

      {selectedSection ? (
        <div className="card">
          <h2 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.75rem" }}>{selectedSection.name}</h2>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: "0.85rem", lineHeight: 1.6, margin: 0 }}>{selectedSection.content}</pre>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {report.sections.map((s) => (
            <div key={s.file} className="card">
              <h2 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.75rem" }}>{s.name}</h2>
              <pre style={{ whiteSpace: "pre-wrap", fontSize: "0.85rem", lineHeight: 1.6, margin: 0 }}>{s.content}</pre>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
