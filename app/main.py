"""FastAPI application with health check endpoint."""

from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Amazon Product Monitoring API",
    version="0.1.0",
)

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Amazon Product Monitoring API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon."""
    favicon_path = Path(__file__).parent / "static" / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return {"error": "favicon not found"}
