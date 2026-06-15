# Web Interface Plan

Add a web UI to TradingAgents while keeping the existing CLI fully intact.

## Architecture

```
Frontend (React + TypeScript + Vite)          Backend (FastAPI)
┌──────────────────────────────┐              ┌────────────────────────┐
│  Dashboard                   │  HTTP/JSON   │  REST API              │
│  Analysis                    │ ◄─────────► │  /api/nepse/*          │
│  Reports                     │  WebSocket   │  /api/analysis/*       │
│  Settings                    │              │  /api/reports/*        │
│                              │              │  /api/settings/*       │
│  shadcn/ui + Tailwind CSS    │              │                        │
└──────────────────────────────┘              │  Celery Worker         │
                                              │  (runs propagate())    │
                                              └───────────┬────────────┘
                                                          │
                                                  Redis (broker + cache)
```

## Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Frontend | React + TypeScript + Vite | Best ecosystem, strong typing |
| UI library | shadcn/ui + Tailwind CSS | Modern, lightweight, customizable |
| Backend | FastAPI | Native async, WebSocket support, Pydantic validation |
| Task queue | Redis + Celery | Production-grade background jobs, retries, persistence |
| Realtime | WebSocket | Low latency, bidirectional |
| Deploy | Docker Compose (or separate) | Flexible, same compose file works locally and on VPS |

## Existing Files — UNCHANGED

| File | Purpose |
|------|---------|
| `cli/main.py` | CLI entry point |
| `scripts/nepse_point.py` | NEPSE index quick check |
| `tradingagents/` | Core Python package |
| `NEPSE_INTEGRATION.md` | NEPSE docs |
| Any other existing file | Unchanged |

## New Files

### Phase 1: Backend Foundation

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, lifespan
│   ├── config.py            # Pydantic BaseSettings
│   ├── dependencies.py      # Redis pool, common deps
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── nepse.py         # GET /api/nepse/index, gainers, losers, turnover, summary
│   │   └── settings.py      # GET/PUT /api/settings
│   └── schemas/
│       ├── __init__.py
│       ├── nepse.py         # IndexResponse, TopStocksResponse, SummaryResponse
│       └── settings.py      # SettingsRequest, SettingsResponse
├── requirements.txt
└── Dockerfile
```

**API endpoints — Phase 1:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/nepse/index` | Current NEPSE index, change, high/low, 52W range |
| GET | `/api/nepse/gainers?limit=5` | Top gainers |
| GET | `/api/nepse/losers?limit=5` | Top losers |
| GET | `/api/nepse/turnover?limit=5` | Top by turnover |
| GET | `/api/nepse/summary` | Market summary (turnover, volume, transactions) |
| GET | `/api/settings` | Get current config |
| PUT | `/api/settings` | Update config / API keys |

### Phase 2: Background Analysis + Realtime

```
backend/app/
├── celery_app.py            # Celery instance
├── routers/
│   └── analysis.py          # POST /api/analysis, GET status, WS /ws/analysis/{id}
├── schemas/
│   └── analysis.py          # AnalysisRequest, AnalysisStatus, ReportResponse
└── tasks/
    ├── __init__.py
    └── analysis_runner.py   # Celery task, progress publisher
```

**API endpoints — Phase 2:**

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/analysis` | Trigger analysis → returns `task_id` |
| GET | `/api/analysis/{task_id}/status` | Poll task status |
| WS | `/ws/analysis/{task_id}` | Real-time progress via WebSocket |
| GET | `/api/analysis/{task_id}/report` | Full report (markdown + JSON) |

**WebSocket message types:**

```json
{"type": "agent_start",    "agent": "market_analyst",         "timestamp": "..."}
{"type": "agent_complete", "agent": "market_analyst",         "summary": "..."}
{"type": "tool_call",      "tool": "get_stock_data",          "args": {...}}
{"type": "progress",       "percent": 50,                     "message": "Team debating..."}
{"type": "complete",       "decision": "BUY",                 "rating": "Overweight"}
{"type": "error",          "message": "API key not configured"}
```

**Analysis flow:**
1. User submits form → `POST /api/analysis` → Celery enqueues task → returns `task_id`
2. Frontend opens WebSocket to `/ws/analysis/{task_id}`
3. Celery worker runs `TradingAgentsGraph.propagate()`, publishes progress messages to Redis pub/sub
4. FastAPI WebSocket handler reads Redis pub/sub channel, forwards to client
5. On completion, worker stores report in `reports/` directory
6. Frontend displays result, user can view full report

### Phase 3: Frontend

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── Layout.tsx           # Sidebar + header + main content
│   │   ├── NEPSEIndexCard.tsx   # Live index display with arrow
│   │   ├── TopStocksTable.tsx   # Reusable table for gainers/losers/turnover
│   │   ├── AnalysisForm.tsx     # Ticker, date, vendor, provider selectors
│   │   ├── ProgressStream.tsx   # Real-time agent progress display
│   │   └── ReportViewer.tsx     # Rendered markdown/decision card
│   ├── pages/
│   │   ├── Dashboard.tsx        # NEPSE index + market overview
│   │   ├── Analysis.tsx         # Form + progress + results
│   │   ├── AnalysisDetail.tsx   # View completed analysis
│   │   ├── Reports.tsx          # Browse historical reports
│   │   └── Settings.tsx         # LLM provider, API keys, vendor config
│   ├── services/
│   │   ├── api.ts               # Axios instance + API functions
│   │   └── websocket.ts         # WebSocket client hooks
│   ├── lib/
│   │   └── utils.ts             # shadcn/ui utilities
│   ├── App.tsx                  # Router
│   └── main.tsx                 # Entry point
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── vite.config.ts
└── Dockerfile
```

**Pages:**

| Route | Page | Content |
|-------|------|---------|
| `/` | Dashboard | NEPSE index card, gainers table, losers table, turnover table, market summary |
| `/analysis` | Analysis | Form to configure + trigger analysis + live progress + results |
| `/analysis/:id` | Analysis Detail | Full report viewer for completed runs |
| `/reports` | Reports | List of all past reports with search/filter |
| `/settings` | Settings | LLM provider selection, API keys, data vendor, default model |

### Phase 4: Docker & Deployment

```
docker-compose.yml   # Backend + Frontend + Redis + Celery Worker
```

```yaml
services:
  redis:        image: redis:7-alpine
  backend:      build: ./backend     (uvicorn app.main:app)
  worker:       build: ./backend     (celery -A app.celery_app worker)
  frontend:     build: ./frontend    (nginx serving built React app)
```

For separate deployment:
- **Backend** → any VPS (DigitalOcean, Hetzner, AWS), `docker compose up backend worker redis`
- **Frontend** → Vercel/Netlify (set `VITE_API_URL` env var pointing to backend)

## Dependencies Added

### Backend (`requirements.txt`)
- `fastapi`
- `uvicorn[standard]`
- `celery[redis]`
- `redis`
- `websockets`
- (the existing `tradingagents` package is already installed)

### Frontend (`package.json`)
- `react`, `react-dom`, `react-router-dom`
- `@radix-ui/*` (shadcn/ui primitives)
- `tailwindcss`, `postcss`, `autoprefixer`
- `lucide-react` (icons)
- `axios`
- `recharts` (optional, for charts)

## Implementation Order

1. Backend Phase 1 — NEPSE + Settings endpoints
2. Backend Phase 2 — Celery + Analysis + WebSocket
3. Frontend Phase 3 — all pages
4. Docker compose + final wiring

## Estimated Effort

- Phase 1: 1 day
- Phase 2: 2-3 days
- Phase 3: 4-6 days
- Phase 4: 1 day
- **Total: ~8-11 days** part-time
