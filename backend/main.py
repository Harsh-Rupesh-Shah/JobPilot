"""
main.py
FastAPI entry point. Configures CORS, includes routers, and handles lifespan events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings

from backend.api.routes import auth, upload, run, stream, applications
from backend.db.collections import setup_indexes
from backend.core.logging_config import setup_logging

# Initialize logging before creating the app
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create DB indexes
    await setup_indexes()
    yield
    # Shutdown logic (if any)

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healthcheck
@app.get("/health")
def health():
    """Simple healthcheck endpoint."""
    return {"status": "ok"}

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(run.router, prefix="", tags=["Run"])
app.include_router(stream.router, prefix="/stream", tags=["Stream"])
app.include_router(applications.router, prefix="/applications", tags=["Applications"])
