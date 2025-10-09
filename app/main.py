"""FastAPI application with health check endpoint."""

from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import get_scalar_api_reference
from supabase import Client, create_client

from app.config import SUPABASE_ANON_KEY, SUPABASE_URL

# 初始化 Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

app = FastAPI(
    title="Amazon Product Monitoring API",
    version="0.1.0",
    description="Amazon 產品監控與優化工具 - 追蹤產品表現、分析競爭對手並提供優化建議",
    # docs_url="/docs" - 使用 Scalar 取代預設的 Swagger UI
    docs_url="/swagger",  # Swagger UI 改為 /swagger (備用)
    redoc_url=None,  # 停用 ReDoc (唯讀，無法測試)
)


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


@app.get(
    "/",
    summary="API 根路徑",
    description="取得 API 基本資訊",
    response_description="API 名稱與版本資訊",
    tags=["System"],
)
async def root():
    """取得 API 基本資訊。

    Returns:
        dict: 包含 API 名稱與版本的字典
    """
    return {"message": "Amazon Product Monitoring API", "version": "0.1.0"}


@app.get(
    "/health",
    summary="健康檢查",
    description="檢查 API 服務與資料庫連線是否正常",
    response_description="服務健康狀態與當前時間戳記",
    tags=["System"],
    responses={
        200: {
            "description": "服務正常運作",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2025-10-07T09:00:00.000000+00:00",
                        "database": "connected",
                    }
                }
            },
        }
    },
)
async def health_check():
    """健康檢查端點。

    用於監控服務是否正常運作，通常由負載平衡器或監控系統呼叫。
    包含資料庫連線測試。

    Returns:
        dict: 包含服務狀態、UTC 時間戳記與資料庫連線狀態
    """
    # 測試 Supabase 連線
    db_status = "connected"
    try:
        supabase.auth.get_session()
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "database": db_status,
    }


@app.get(
    "/favicon.ico",
    include_in_schema=False,
)
async def favicon():
    """提供網站圖示（不顯示於 API 文件中）。"""
    favicon_path = Path(__file__).parent / "static" / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return {"error": "favicon not found"}
