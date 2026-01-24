"""Main application entry point."""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from app.adapters.rest_api import users, readings, admin
from app.container import Container
from app.adapters.sqla.mapping import bind_mappers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup: Initialize container
    container = Container()
    container.init_resources()

    yield

    # Shutdown: Close database connections
    await container.shutdown_resources()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Bind ORM mappers
    bind_mappers()

    app = FastAPI(
        title="СТ АВТО учет показаний эл. энергии API",
        description="API for electricity meter reading management",
        version="1.0.0",
        lifespan=lifespan
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(users.router, prefix="/api", tags=["users"])
    app.include_router(readings.router, prefix="/api", tags=["readings"])
    app.include_router(admin.router, prefix="/api", tags=["admin"])

    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint."""
        return {
            "message": "СТ АВТО учет показаний эл. энергии API",
            "version": "1.0.0",
            "docs": "/docs"
        }

    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )