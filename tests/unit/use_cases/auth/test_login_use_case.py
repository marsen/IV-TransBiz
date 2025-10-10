"""Unit tests for LoginUseCase."""

from unittest.mock import Mock

import pytest

from app.use_cases.auth.login_use_case import LoginUseCase


def test_login_use_case_success():
    """測試登入成功。"""
    # Arrange - 準備測試資料和依賴
    login_data = {"email": "test@example.com", "password": "password123"}
    expected_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    expected_user_id = "123e4567-e89b-12d3-a456-426614174000"
    expected_email = "test@example.com"
    mock_supabase = Mock()
    mock_supabase.auth.sign_in_with_password.return_value = Mock(
        session=Mock(access_token=expected_access_token),
        user=Mock(id=expected_user_id, email=expected_email),
    )
    target = LoginUseCase(supabase_client=mock_supabase)

    # Act - 執行受測操作
    result = target.execute(email=login_data["email"], password=login_data["password"])

    # Assert - 驗證結果
    assert result.access_token == expected_access_token
    assert result.user.id == expected_user_id
    assert result.user.email == expected_email
    mock_supabase.auth.sign_in_with_password.assert_called_once_with(login_data)


def test_login_use_case_invalid_credentials():
    """測試登入失敗 - 無效憑證。"""
    # Arrange - 準備測試資料和依賴
    login_data = {"email": "test@example.com", "password": "wrongpassword"}
    error_message = "Invalid login credentials"
    mock_supabase = Mock()
    mock_supabase.auth.sign_in_with_password.side_effect = Exception(error_message)
    target = LoginUseCase(supabase_client=mock_supabase)

    # Act & Assert - 執行並驗證拋出例外
    with pytest.raises(Exception) as exc_info:
        target.execute(email=login_data["email"], password=login_data["password"])

    # Assert - 驗證例外訊息
    assert error_message in str(exc_info.value)
    mock_supabase.auth.sign_in_with_password.assert_called_once_with(login_data)
