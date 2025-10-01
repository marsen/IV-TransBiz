"""FastAPI application with health check endpoint."""

from datetime import datetime

from fastapi import FastAPI

app = FastAPI(
    title="Amazon Product Monitoring API",
    version="0.1.0",
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Amazon Product Monitoring API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
