import { useEffect, useState } from "react"
import { api, SettingsData } from "../services/api"

export function Settings() {
  const [settings, setSettings] = useState<SettingsData | null>(null)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState<Record<string, string>>({})

  useEffect(() => {
    api.settings().then((s) => {
      setSettings(s)
      setForm({
        llm_provider: s.llm_provider,
        deep_think_llm: s.deep_think_llm,
        quick_think_llm: s.quick_think_llm,
        data_vendor: s.data_vendor,
      })
    })
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      const updated = await api.updateSettings(form)
      setSettings(updated)
    } catch (e: any) {
      alert("Failed to save: " + e.message)
    }
    setSaving(false)
  }

  if (!settings) return <div>Loading...</div>

  const rows = [
    { label: "LLM Provider", key: "llm_provider", type: "select", options: ["openrouter", "deepseek", "openai", "google", "anthropic"] },
    { label: "Deep Think Model", key: "deep_think_llm", type: "text" },
    { label: "Quick Think Model", key: "quick_think_llm", type: "text" },
    { label: "Data Vendor", key: "data_vendor", type: "select", options: ["nepse", "yfinance"] },
  ]

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem" }}>Settings</h1>
      <div className="card" style={{ maxWidth: 500 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {rows.map((r) => (
            <div key={r.key}>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--muted-foreground)", marginBottom: "0.25rem" }}>{r.label}</label>
              {r.type === "select" ? (
                <select className="select" value={form[r.key] || ""} onChange={(e) => setForm({ ...form, [r.key]: e.target.value })}>
                  {r.options?.map((o) => <option key={o} value={o}>{o}</option>)}
                </select>
              ) : (
                <input className="input" value={form[r.key] || ""} onChange={(e) => setForm({ ...form, [r.key]: e.target.value })} />
              )}
            </div>
          ))}
          <button className="btn" onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </div>
      </div>

      <h2 style={{ fontSize: "1rem", fontWeight: 600, margin: "2rem 0 0.75rem" }}>API Keys</h2>
      <div className="card" style={{ maxWidth: 500 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", fontSize: "0.875rem" }}>
          {[
            { label: "OpenRouter", key: "openrouter_api_key_set" },
            { label: "DeepSeek", key: "deepseek_api_key_set" },
            { label: "OpenAI", key: "openai_api_key_set" },
            { label: "Google Gemini", key: "google_api_key_set" },
            { label: "Anthropic", key: "anthropic_api_key_set" },
          ].map((item) => (
            <div key={item.key} style={{ display: "flex", justifyContent: "space-between" }}>
              <span>{item.label}</span>
              <span style={{ color: (settings as any)[item.key] ? "var(--success)" : "var(--destructive)" }}>
                {(settings as any)[item.key] ? "✓ Configured" : "Not set"}
              </span>
            </div>
          ))}
        </div>
        <p style={{ fontSize: "0.75rem", color: "var(--muted-foreground)", marginTop: "0.75rem" }}>
          API keys are read from the <code>.env</code> file. To update, edit <code>.env</code> and restart the server.
        </p>
      </div>
    </div>
  )
}
