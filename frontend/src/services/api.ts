const API_BASE = "/api"

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...opts?.headers },
    ...opts,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${res.status}: ${body}`)
  }
  return res.json()
}

export interface IndexData {
  name: string
  current_value: number
  change: number
  per_change: number
  high: number
  low: number
  fifty_two_week_high: number
  fifty_two_week_low: number
  generated_time: string
}

export interface TopStockItem {
  symbol: string
  security_name: string
  ltp: number | null
  point_change: number | null
  percentage_change: number | null
  turnover: number | null
  closing_price: number | null
}

export interface SummaryItem {
  detail: string
  value: number
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

export interface SettingsData {
  llm_provider: string
  deep_think_llm: string
  quick_think_llm: string
  data_vendor: string
  openrouter_api_key_set: boolean
  deepseek_api_key_set: boolean
  openai_api_key_set: boolean
  google_api_key_set: boolean
  anthropic_api_key_set: boolean
}

export interface AnalysisStatus {
  task_id: string
  status: string
  progress: number
  message: string
  ticker: string
  error: string | null
}

export interface ReportSection {
  name: string
  file: string
}

export interface ReportEntry {
  ticker: string
  date: string
  sections: ReportSection[]
}

export interface ReportSectionContent extends ReportSection {
  content: string
}

export interface ReportDetail {
  ticker: string
  date: string
  sections: ReportSectionContent[]
}

export const api = {
  index: () => request<ApiResponse<IndexData>>("/nepse/index"),
  gainers: (limit = 5) => request<ApiResponse<TopStockItem[]>>(`/nepse/gainers?limit=${limit}`),
  losers: (limit = 5) => request<ApiResponse<TopStockItem[]>>(`/nepse/losers?limit=${limit}`),
  turnover: (limit = 5) => request<ApiResponse<TopStockItem[]>>(`/nepse/turnover?limit=${limit}`),
  summary: () => request<ApiResponse<SummaryItem[]>>("/nepse/summary"),
  settings: () => request<SettingsData>("/settings"),
  updateSettings: (body: Record<string, unknown>) => request<SettingsData>("/settings", { method: "PUT", body: JSON.stringify(body) }),
  startAnalysis: (body: { ticker: string; date?: string; vendor?: string; llm_provider?: string }) =>
    request<AnalysisStatus>("/analysis", { method: "POST", body: JSON.stringify(body) }),
  analysisStatus: (taskId: string) => request<AnalysisStatus>(`/analysis/${taskId}/status`),
  analysisReport: (taskId: string) => request<Record<string, any>>(`/analysis/${taskId}/report`),
  reportsList: () => request<ReportEntry[]>("/reports"),
  reportDetail: (ticker: string, date: string) => request<ReportDetail>(`/reports/${ticker}/${date}`),
}
