import { TopStockItem } from "../services/api"
import { formatNumber } from "../lib/utils"

interface Props {
  title: string
  items: TopStockItem[]
  type: "gainer" | "loser" | "turnover"
}

export function TopStocksTable({ title, items, type }: Props) {
  return (
    <div className="card" style={{ flex: 1 }}>
      <h3 style={{ fontSize: "0.875rem", fontWeight: 600, margin: "0 0 0.75rem" }}>{title}</h3>
      <table className="table-auto">
        <thead>
          <tr>
            <th>Symbol</th>
            {type !== "turnover" && <th style={{ textAlign: "right" }}>LTP</th>}
            {type === "gainer" && <th style={{ textAlign: "right" }}>Change</th>}
            {type === "loser" && <th style={{ textAlign: "right" }}>Change</th>}
            {type !== "turnover" && <th style={{ textAlign: "right" }}>%</th>}
            {type === "turnover" && <th style={{ textAlign: "right" }}>Turnover</th>}
            {type === "turnover" && <th style={{ textAlign: "right" }}>Price</th>}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.symbol}>
              <td style={{ fontWeight: 500 }}>{item.symbol}</td>
              {type !== "turnover" && <td style={{ textAlign: "right" }}>{item.ltp != null ? formatNumber(item.ltp) : "-"}</td>}
              {(type === "gainer" || type === "loser") && (
                <td style={{ textAlign: "right", color: item.point_change != null && item.point_change >= 0 ? "var(--success)" : "var(--destructive)" }}>
                  {item.point_change != null ? (item.point_change >= 0 ? "+" : "") + formatNumber(item.point_change) : "-"}
                </td>
              )}
              {type !== "turnover" && (
                <td style={{ textAlign: "right", color: item.percentage_change != null && item.percentage_change >= 0 ? "var(--success)" : "var(--destructive)" }}>
                  {item.percentage_change != null ? (item.percentage_change >= 0 ? "+" : "") + formatNumber(item.percentage_change) + "%" : "-"}
                </td>
              )}
              {type === "turnover" && (
                <td style={{ textAlign: "right" }}>{item.turnover != null ? formatNumber(item.turnover) : "-"}</td>
              )}
              {type === "turnover" && (
                <td style={{ textAlign: "right" }}>{item.closing_price != null ? formatNumber(item.closing_price) : "-"}</td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
