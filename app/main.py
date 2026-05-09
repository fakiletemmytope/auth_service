from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from app.database import init_db, engine
from app.routers import auth, admin




@asynccontextmanager
async def lifespan(FastAPI):
    

    await init_db()
    print("Database initialized")

    yield

    try:
        await engine.dispose()
    except Exception as e:
        print(f"Error disposing database engine: {e}")
    finally:
        await engine.dispose()
        print("Database engine disposed")


app = FastAPI(lifespan=lifespan)

# Add middleware
app.add_middleware(RequestCorrelationMiddleware)

# Include routers
app.include_router(auth.router, tags=["auth"])
app.include_router(admin.router, tags=["admin"])


@app.get("/health")
async def health():
    logger.debug("Health check endpoint called")
    return {"status": "healthy"}



