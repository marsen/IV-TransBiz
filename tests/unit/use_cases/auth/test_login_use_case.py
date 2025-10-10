"""Unit tests for LoginUseCase."""

from unittest.mock import Mock

import pytest

from app.domain.entities.user import User
from app.use_cases.auth.login_use_case import LoginUseCase


def test_login_use_case_success():
    """測試登入成功。"""
    # Arrange - 準備測試資料和依賴
    email = "test@example.com"
    password = "password123"
    expected_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    expected_user = User(id="123e4567-e89b-12d3-a456-426614174000", email=email)
    mock_auth_repo = Mock()
    mock_auth_repo.login.return_value = (expected_access_token, expected_user)
    target = LoginUseCase(auth_repo=mock_auth_repo)

    # Act - 執行受測操作
    result = target.execute(email=email, password=password)

    # Assert - 驗證結果
    assert result.access_token == expected_access_token
    assert result.user.id == expected_user.id
    assert result.user.email == expected_user.email
    mock_auth_repo.login.assert_called_once_with(email, password)


def test_login_use_case_invalid_credentials():
    """測試登入失敗 - 無效憑證。"""
    # Arrange - 準備測試資料和依賴
    email = "test@example.com"
    password = "wrongpassword"
    error_message = "Invalid login credentials"
    mock_auth_repo = Mock()
    mock_auth_repo.login.side_effect = Exception(error_message)
    target = LoginUseCase(auth_repo=mock_auth_repo)

    # Act & Assert - 執行並驗證拋出例外
    with pytest.raises(Exception) as exc_info:
        target.execute(email=email, password=password)

    # Assert - 驗證例外訊息
    assert error_message in str(exc_info.value)
    mock_auth_repo.login.assert_called_once_with(email, password)
