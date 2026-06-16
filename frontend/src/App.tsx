import { BrowserRouter, Routes, Route } from "react-router-dom"
import { Layout } from "./components/Layout"
import { Dashboard } from "./pages/Dashboard"
import { Analysis } from "./pages/Analysis"
import { AnalysisDetail } from "./pages/AnalysisDetail"
import { Reports } from "./pages/Reports"
import { ReportDetail } from "./pages/ReportDetail"
import { Settings } from "./pages/Settings"

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/analysis/:id" element={<AnalysisDetail />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/reports/:ticker/:date" element={<ReportDetail />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
