"""Authentication API schemas - Request/Response models."""

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """使用者資料回應。"""

    id: str
    email: str


class SignupRequest(BaseModel):
    """註冊請求。"""

    email: EmailStr
    password: str


class SignupResponse(BaseModel):
    """註冊回應。"""

    user: UserResponse
    message: str


class LoginRequest(BaseModel):
    """登入請求。"""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """登入回應。"""

    access_token: str
    user: UserResponse
