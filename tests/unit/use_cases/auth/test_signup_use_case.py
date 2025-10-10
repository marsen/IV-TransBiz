"""Unit tests for SignupUseCase."""

from unittest.mock import Mock

import pytest

from app.use_cases.auth.signup_use_case import SignupUseCase


def test_signup_use_case_success():
    """測試註冊成功。"""
    # Arrange - 準備測試資料和依賴
    signup_data = {"email": "test@example.com", "password": "password123"}
    expected_user_id = "123e4567-e89b-12d3-a456-426614174000"
    expected_email = "test@example.com"
    mock_supabase = Mock()
    mock_supabase.auth.sign_up.return_value = Mock(
        user=Mock(id=expected_user_id, email=expected_email)
    )
    target = SignupUseCase(supabase_client=mock_supabase)

    # Act - 執行受測操作
    result = target.execute(email=signup_data["email"], password=signup_data["password"])

    # Assert - 驗證結果
    assert result.user.id == expected_user_id
    assert result.user.email == expected_email
    assert result.message == "User created successfully"
    mock_supabase.auth.sign_up.assert_called_once_with(signup_data)


def test_signup_use_case_email_already_exists():
    """測試註冊失敗 - Email 已存在。"""
    # Arrange - 準備測試資料和依賴
    signup_data = {"email": "existing@example.com", "password": "password123"}
    error_message = "User already registered"
    mock_supabase = Mock()
    mock_supabase.auth.sign_up.side_effect = Exception(error_message)
    target = SignupUseCase(supabase_client=mock_supabase)

    # Act & Assert - 執行並驗證拋出例外
    with pytest.raises(Exception) as exc_info:
        target.execute(email=signup_data["email"], password=signup_data["password"])

    # Assert - 驗證例外訊息
    assert error_message in str(exc_info.value)
    mock_supabase.auth.sign_up.assert_called_once_with(signup_data)
