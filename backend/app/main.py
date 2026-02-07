from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.models import *  # noqa: F401,F403 — ensure all models are registered
from app.routers import (
    engagements,
    parties,
    goods_services,
    failure_modes,
    loss_scenarios,
    mitigations,
    quantification,
    dashboard,
    ai_generation,
)

app = FastAPI(title="Contract Risk Quantification Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(engagements.router)
app.include_router(parties.router)
app.include_router(goods_services.router)
app.include_router(failure_modes.router)
app.include_router(loss_scenarios.router)
app.include_router(mitigations.router)
app.include_router(quantification.router)
app.include_router(dashboard.router)
app.include_router(ai_generation.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
