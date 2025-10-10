"""User entity."""

from dataclasses import dataclass


@dataclass
class User:
    """使用者實體（從 JWT payload 建立）。"""

    id: str
    email: str

    @classmethod
    def from_jwt_payload(cls, payload: dict) -> "User":
        """從 JWT payload 建立 User 實體。

        Args:
            payload: JWT token payload，包含 sub 和 email

        Returns:
            User 實體
        """
        return cls(
            id=payload["sub"],
            email=payload["email"],
        )
