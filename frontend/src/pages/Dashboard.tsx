import { useEffect, useState } from "react"
import { api, TopStockItem, SummaryItem } from "../services/api"
import { NEPSEIndexCard } from "../components/NEPSEIndexCard"
import { TopStocksTable } from "../components/TopStocksTable"
import { formatNumber } from "../lib/utils"

export function Dashboard() {
  const [gainers, setGainers] = useState<TopStockItem[]>([])
  const [losers, setLosers] = useState<TopStockItem[]>([])
  const [turnover, setTurnover] = useState<TopStockItem[]>([])
  const [summary, setSummary] = useState<SummaryItem[]>([])

  useEffect(() => {
    api.gainers().then((r) => { if (r.success && r.data) setGainers(r.data) })
    api.losers().then((r) => { if (r.success && r.data) setLosers(r.data) })
    api.turnover().then((r) => { if (r.success && r.data) setTurnover(r.data) })
    api.summary().then((r) => { if (r.success && r.data) setSummary(r.data) })
  }, [])

  const smap = Object.fromEntries(summary.map((s) => [s.detail, s.value]))

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Dashboard</h1>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem" }}>
        <NEPSEIndexCard />
        <div className="card">
          <h3 style={{ fontSize: "0.875rem", fontWeight: 600, margin: "0 0 0.75rem" }}>Market Summary</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", fontSize: "0.875rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--muted-foreground)" }}>Turnover</span>
              <span style={{ fontWeight: 500 }}>NPR {formatNumber((smap["Total Turnover Rs:"] || 0) / 1e9)}B</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--muted-foreground)" }}>Volume</span>
              <span style={{ fontWeight: 500 }}>{formatNumber(smap["Total Traded Shares"] || 0, 0)} shares</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--muted-foreground)" }}>Transactions</span>
              <span style={{ fontWeight: 500 }}>{formatNumber(smap["Total Transactions"] || 0, 0)}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--muted-foreground)" }}>Scrips Traded</span>
              <span style={{ fontWeight: 500 }}>{formatNumber(smap["Total Scrips Traded"] || 0, 0)}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--muted-foreground)" }}>Market Cap</span>
              <span style={{ fontWeight: 500 }}>NPR {formatNumber((smap["Total Market Capitalization Rs:"] || 0) / 1e9)}B</span>
            </div>
          </div>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem" }}>
        <TopStocksTable title="Top Gainers" items={gainers} type="gainer" />
        <TopStocksTable title="Top Losers" items={losers} type="loser" />
        <TopStocksTable title="Top by Turnover" items={turnover} type="turnover" />
      </div>
    </div>
  )
}
