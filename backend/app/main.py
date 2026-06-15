import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.routers import nepse, settings as settings_router, analysis

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting TradingAgents backend")
    yield
    logging.info("Shutting down TradingAgents backend")


app = FastAPI(title="TradingAgents API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nepse.router)
app.include_router(settings_router.router)
app.include_router(analysis.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
