"""Health Check use case - 處理健康檢查邏輯。"""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.use_cases.health.ports import DatabaseRepository


@dataclass
class HealthCheckResult:
    """健康檢查結果。"""

    status: str
    database: str
    timestamp: datetime


class HealthCheckUseCase:
    """健康檢查 Use Case - 主程式邏輯。"""

    def __init__(self, db_repo: DatabaseRepository):
        """初始化 HealthCheckUseCase.

        Args:
            db_repo: Database Repository 實例（依賴抽象）
        """
        self.db_repo = db_repo

    def execute(self) -> HealthCheckResult:
        """執行健康檢查邏輯。

        Returns:
            HealthCheckResult: 健康檢查結果
        """
        # 檢查資料庫連線
        db_status = self.db_repo.check_connection()

        # 返回結果
        return HealthCheckResult(
            status="healthy",
            database=db_status,
            timestamp=datetime.now(UTC),
        )
