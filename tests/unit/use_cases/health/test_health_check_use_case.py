"""Unit tests for HealthCheckUseCase."""

from datetime import datetime
from unittest.mock import Mock

from app.use_cases.health.health_check_use_case import HealthCheckUseCase


def test_health_check_use_case_success():
    """測試 health check 成功（資料庫連線正常）。"""
    # Arrange - 準備測試資料和依賴
    expected_db_status = "connected"
    mock_db_repo = Mock()
    mock_db_repo.check_connection.return_value = expected_db_status
    target = HealthCheckUseCase(db_repo=mock_db_repo)

    # Act - 執行受測操作
    result = target.execute()

    # Assert - 驗證結果
    assert result.status == "healthy"
    assert result.database == expected_db_status
    assert isinstance(result.timestamp, datetime)
    mock_db_repo.check_connection.assert_called_once()
