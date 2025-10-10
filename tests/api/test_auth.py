"""Unit tests for authentication API endpoints."""

from unittest.mock import Mock


def test_signup_success(client, mock_supabase):
    """測試註冊成功。"""
    # Arrange - 準備測試資料和依賴
    expected_user_id = "123e4567-e89b-12d3-a456-426614174000"
    expected_email = "test@example.com"
    signup_data = {
        "email": expected_email,
        "password": "password123",
    }
    expected_response = {
        "user": {
            "id": expected_user_id,
            "email": expected_email,
        },
        "message": "User created successfully",
    }
    mock_supabase.auth.sign_up.return_value = Mock(
        user=Mock(
            id=expected_user_id,
            email=expected_email,
        )
    )
    target = client

    # Act - 執行受測操作
    response = target.post("/api/v1/auth/signup", json=signup_data)

    # Assert - 驗證結果
    assert response.status_code == 201
    assert response.json() == expected_response
    mock_supabase.auth.sign_up.assert_called_once_with(signup_data)


def test_signup_email_already_exists(client, mock_supabase):
    """測試註冊失敗 - email 已存在。"""
    # Arrange - 準備測試資料和依賴
    signup_data = {
        "email": "existing@example.com",
        "password": "password123",
    }
    error_message = "User already registered"
    mock_supabase.auth.sign_up.side_effect = Exception(error_message)
    target = client

    # Act - 執行受測操作
    response = target.post("/api/v1/auth/signup", json=signup_data)

    # Assert - 驗證結果
    assert response.status_code == 400
    assert error_message.lower() in response.json()["detail"].lower()
