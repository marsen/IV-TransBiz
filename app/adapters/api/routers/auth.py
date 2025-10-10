"""Authentication API router - Thin adapter layer."""

from fastapi import APIRouter, HTTPException, status

from app.adapters.api.schemas.auth import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    SignupResponse,
    UserResponse,
)
from app.adapters.repositories.supabase_auth_repository import (
    SupabaseAuthRepository,
)
from app.infrastructure.supabase_client import get_supabase_client
from app.use_cases.auth.login_use_case import LoginUseCase
from app.use_cases.auth.signup_use_case import SignupUseCase

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# 建立 Supabase client 和 Repository（module level singleton）
supabase = get_supabase_client()
auth_repository = SupabaseAuthRepository(supabase_client=supabase)


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="使用者註冊",
)
async def signup(request: SignupRequest) -> SignupResponse:
    """使用者註冊端點。"""
    try:
        use_case = SignupUseCase(auth_repo=auth_repository)
        result = use_case.execute(email=request.email, password=request.password)
        return SignupResponse(
            user=UserResponse(id=result.user.id, email=result.user.email),
            message=result.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="使用者登入",
)
async def login(request: LoginRequest) -> LoginResponse:
    """使用者登入端點。"""
    try:
        use_case = LoginUseCase(auth_repo=auth_repository)
        result = use_case.execute(email=request.email, password=request.password)
        return LoginResponse(
            access_token=result.access_token,
            user=UserResponse(id=result.user.id, email=result.user.email),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e
