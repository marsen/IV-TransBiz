"""Unit tests for SignupUseCase."""

from unittest.mock import Mock

import pytest

from app.domain.entities.user import User
from app.use_cases.auth.signup_use_case import SignupUseCase


def test_signup_use_case_success():
    """測試註冊成功。"""
    # Arrange - 準備測試資料和依賴
    email = "test@example.com"
    password = "password123"
    expected_user = User(id="123e4567-e89b-12d3-a456-426614174000", email=email)
    mock_auth_repo = Mock()
    mock_auth_repo.signup.return_value = expected_user
    target = SignupUseCase(auth_repo=mock_auth_repo)

    # Act - 執行受測操作
    result = target.execute(email=email, password=password)

    # Assert - 驗證結果
    assert result.user.id == expected_user.id
    assert result.user.email == expected_user.email
    assert result.message == "User created successfully"
    mock_auth_repo.signup.assert_called_once_with(email, password)


def test_signup_use_case_email_already_exists():
    """測試註冊失敗 - Email 已存在。"""
    # Arrange - 準備測試資料和依賴
    email = "existing@example.com"
    password = "password123"
    error_message = "User already registered"
    mock_auth_repo = Mock()
    mock_auth_repo.signup.side_effect = Exception(error_message)
    target = SignupUseCase(auth_repo=mock_auth_repo)

    # Act & Assert - 執行並驗證拋出例外
    with pytest.raises(Exception) as exc_info:
        target.execute(email=email, password=password)

    # Assert - 驗證例外訊息
    assert error_message in str(exc_info.value)
    mock_auth_repo.signup.assert_called_once_with(email, password)
