"""Health check API router - Thin adapter layer."""

from fastapi import APIRouter

from app.adapters.repositories.supabase_database_repository import (
    SupabaseDatabaseRepository,
)
from app.infrastructure.supabase_client import get_supabase_client
from app.use_cases.health.health_check_use_case import HealthCheckUseCase

router = APIRouter(tags=["System"])

# 建立 Supabase client 和 Repository（module level singleton）
supabase = get_supabase_client()
db_repository = SupabaseDatabaseRepository(supabase_client=supabase)


@router.get(
    "/health",
    summary="健康檢查",
    description="檢查 API 服務與資料庫連線是否正常",
    response_description="服務健康狀態與當前時間戳記",
)
async def health_check():
    """健康檢查端點。

    用於監控服務是否正常運作，通常由負載平衡器或監控系統呼叫。
    包含資料庫連線測試。

    Returns:
        dict: 包含服務狀態、資料庫連線狀態與 UTC 時間戳記
    """
    use_case = HealthCheckUseCase(db_repo=db_repository)
    result = use_case.execute()

    return {
        "status": result.status,
        "database": result.database,
        "timestamp": result.timestamp.isoformat(),
    }
