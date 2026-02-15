"""FastAPI app entrypoint for LifeOS 0-21 backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import daily_plan, milestones, tasks, users


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create DB tables at startup for local bootstrap.

    In production, replace with Alembic migrations.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="LifeOS 0-21 API",
    version="0.2.0",
    description="Backend API for child profiles, AI daily planning, and task progress.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    """Basic health route for service checks."""
    return {"status": "ok", "service": "LifeOS 0-21 API"}


app.include_router(users.router)
app.include_router(daily_plan.router)
app.include_router(tasks.router)
app.include_router(milestones.router)
