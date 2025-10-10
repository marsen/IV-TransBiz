"""Unit tests for User entity."""


def test_user_creation():
    """測試建立 User 實體。"""
    from app.domain.entities.user import User

    user = User(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@example.com",
    )

    assert user.id == "123e4567-e89b-12d3-a456-426614174000"
    assert user.email == "test@example.com"


def test_user_from_jwt_payload():
    """測試從 JWT payload 建立 User。"""
    from app.domain.entities.user import User

    payload = {
        "sub": "123e4567-e89b-12d3-a456-426614174000",
        "email": "test@example.com",
        "aud": "authenticated",
    }

    user = User.from_jwt_payload(payload)

    assert user.id == "123e4567-e89b-12d3-a456-426614174000"
    assert user.email == "test@example.com"
