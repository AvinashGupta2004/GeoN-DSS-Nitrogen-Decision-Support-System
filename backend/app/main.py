"""
GeoN-DSS FastAPI Application Entry Point
=========================================
Nitrogen Decision Support System — Uttar Pradesh
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import predict, field, health

app = FastAPI(
    title="GeoN-DSS API",
    description="Geospatial Nitrogen Decision Support System for Uttar Pradesh",
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(field.router, prefix="/api/v1", tags=["field"])
app.include_router(predict.router, prefix="/api/v1", tags=["predict"])


@app.get("/")
def root():
    return {"message": "GeoN-DSS API is running", "docs": "/docs"}
