"""FastAPI main application for Todo Full-Stack Web Application.

This module initializes the FastAPI app, configures CORS middleware,
and mounts authentication and tasks routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import init_db
from backend.routers import auth, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events (startup/shutdown)."""
    # Startup: Initialize database schema
    print(">>> Starting up Todo application...")
    await init_db()
    print(">>> Application startup complete")

    yield

    # Shutdown: Cleanup resources
    print(">>> Shutting down Todo application...")


# Initialize FastAPI application
app = FastAPI(
    title="Todo Full-Stack Web Application API",
    description="RESTful API for multi-user todo application with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development server
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers (including Authorization)
)

# Mount routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check."""
    return {
        "status": "healthy",
        "message": "Todo Full-Stack Web Application API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}
