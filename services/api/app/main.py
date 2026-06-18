from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin_api.routes import router as admin_router
from app.config import settings
from app.public_api.assessments import router as assessments_router
from app.public_api.documents import router as documents_router
from app.public_api.pages import router as pages_router
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(
    title="EU AI Act Compliance Navigator API",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assessments_router, prefix="/api/v1")
app.include_router(pages_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
async def healthz() -> HealthResponse:
    return HealthResponse(status="ok", version="0.2.0")


@app.get("/readyz", response_model=HealthResponse, tags=["health"])
async def readyz() -> HealthResponse:
    return HealthResponse(status="ok", version="0.2.0")
