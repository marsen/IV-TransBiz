"""System router - API root and static resources."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["System"])


@router.get(
    "/",
    summary="API 根路徑",
    description="取得 API 基本資訊",
    response_description="API 名稱與版本資訊",
)
async def root():
    """取得 API 基本資訊。

    Returns:
        dict: 包含 API 名稱與版本的字典
    """
    return {"message": "Amazon Product Monitoring API", "version": "0.1.0"}


@router.get(
    "/favicon.ico",
    include_in_schema=False,
)
async def favicon():
    """提供網站圖示（不顯示於 API 文件中）。"""
    favicon_path = Path(__file__).parent.parent.parent.parent / "static" / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return {"error": "favicon not found"}
