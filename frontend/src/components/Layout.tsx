import { Link, useLocation } from "react-router-dom"
import { ReactNode } from "react"

const navItems = [
  { to: "/", label: "Dashboard", icon: "📊" },
  { to: "/analysis", label: "Analysis", icon: "🔍" },
  { to: "/reports", label: "Reports", icon: "📄" },
  { to: "/settings", label: "Settings", icon: "⚙️" },
]

export function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <nav style={{ width: 220, background: "var(--card)", borderRight: "1px solid var(--border)", padding: "1rem" }}>
        <div style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "2rem", color: "var(--primary)" }}>
          TradingAgents
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                padding: "0.5rem 0.75rem",
                borderRadius: "0.5rem",
                textDecoration: "none",
                color: location.pathname === item.to ? "var(--primary)" : "var(--muted-foreground)",
                background: location.pathname === item.to ? "var(--muted)" : "transparent",
                fontSize: "0.875rem",
              }}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </div>
      </nav>
      <main style={{ flex: 1, padding: "1.5rem", overflowY: "auto" }}>
        {children}
      </main>
    </div>
  )
}
