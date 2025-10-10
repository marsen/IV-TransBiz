"""Unit tests for authentication API endpoints."""

from unittest.mock import Mock


def test_signup_success(client, mock_supabase):
    """測試註冊成功。"""
    # Arrange - 準備測試資料和 mock
    mock_supabase.auth.sign_up.return_value = Mock(
        user=Mock(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
        )
    )
    target = client

    # Act - 執行受測操作
    response = target.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    # Assert - 驗證結果
    assert response.status_code == 201
    assert response.json() == {
        "user": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
        },
        "message": "User created successfully",
    }
    mock_supabase.auth.sign_up.assert_called_once_with(
        {"email": "test@example.com", "password": "password123"}
    )


def test_signup_email_already_exists(client, mock_supabase):
    """測試註冊失敗 - email 已存在。"""
    # Arrange
    mock_supabase.auth.sign_up.side_effect = Exception("User already registered")
    target = client

    # Act
    response = target.post(
        "/api/v1/auth/signup",
        json={
            "email": "existing@example.com",
            "password": "password123",
        },
    )

    # Assert
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()
