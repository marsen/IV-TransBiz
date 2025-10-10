"""FastAPI application - Clean Architecture entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import get_scalar_api_reference

from app.adapters.api.routers import auth, health, system

app = FastAPI(
    title="Amazon Product Monitoring API",
    version="0.1.0",
    description="Amazon 產品監控與優化工具 - 追蹤產品表現、分析競爭對手並提供優化建議",
    # docs_url="/docs" - 使用 Scalar 取代預設的 Swagger UI
    docs_url="/swagger",  # Swagger UI 改為 /swagger (備用)
    redoc_url=None,  # 停用 ReDoc (唯讀，無法測試)
)

# 註冊 routers
app.include_router(system.router)
app.include_router(health.router)
app.include_router(auth.router)


@app.get("/docs", include_in_schema=False)
async def scalar_docs():
    """API 文件 - 使用 Scalar (現代化 UI，支援互動測試)。"""
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
