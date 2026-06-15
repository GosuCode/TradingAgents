import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { api } from "../services/api"
import { ReportViewer } from "../components/ReportViewer"

export function AnalysisDetail() {
  const { id } = useParams<{ id: string }>()
  const [report, setReport] = useState<any>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!id) return
    api.analysisReport(id).then((r) => {
      if (r && r.ticker) setReport(r)
      else setError("Report not found or not yet completed")
    }).catch((e) => setError(e.message))
  }, [id])

  if (error) return <div style={{ color: "var(--destructive)" }}>{error}</div>
  if (!report) return <div>Loading...</div>

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Analysis Report</h1>
      <ReportViewer
        decision={report.decision}
        rating={report.rating}
        summary={report.summary}
        ticker={report.ticker}
        date={report.date}
      />
    </div>
  )
}
