import { useState } from "react"

interface Props {
  onStart: (data: { ticker: string; date: string; vendor: string; llm_provider: string }) => void
  disabled?: boolean
}

export function AnalysisForm({ onStart, disabled }: Props) {
  const [ticker, setTicker] = useState("")
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [vendor, setVendor] = useState("nepse")
  const [provider, setProvider] = useState("openrouter")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!ticker.trim()) return
    onStart({ ticker: ticker.trim().toUpperCase(), date, vendor, llm_provider: provider })
  }

  return (
    <form onSubmit={handleSubmit} className="card" style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: 500 }}>
      <h2 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 600 }}>Start New Analysis</h2>
      <div>
        <label style={{ display: "block", fontSize: "0.8rem", color: "var(--muted-foreground)", marginBottom: "0.25rem" }}>Ticker</label>
        <input className="input" placeholder="e.g. NABIL, CYCL" value={ticker} onChange={(e) => setTicker(e.target.value)} required />
      </div>
      <div>
        <label style={{ display: "block", fontSize: "0.8rem", color: "var(--muted-foreground)", marginBottom: "0.25rem" }}>Date</label>
        <input className="input" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
      </div>
      <div style={{ display: "flex", gap: "1rem" }}>
        <div style={{ flex: 1 }}>
          <label style={{ display: "block", fontSize: "0.8rem", color: "var(--muted-foreground)", marginBottom: "0.25rem" }}>Data Vendor</label>
          <select className="select" value={vendor} onChange={(e) => setVendor(e.target.value)}>
            <option value="nepse">NEPSE</option>
            <option value="yfinance">Yahoo Finance</option>
          </select>
        </div>
        <div style={{ flex: 1 }}>
          <label style={{ display: "block", fontSize: "0.8rem", color: "var(--muted-foreground)", marginBottom: "0.25rem" }}>LLM Provider</label>
          <select className="select" value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="openrouter">OpenRouter</option>
            <option value="deepseek">DeepSeek</option>
            <option value="google">Google Gemini</option>
            <option value="openai">OpenAI</option>
          </select>
        </div>
      </div>
      <button className="btn" type="submit" disabled={disabled || !ticker.trim()}>
        {disabled ? "Running..." : "Start Analysis"}
      </button>
    </form>
  )
}
