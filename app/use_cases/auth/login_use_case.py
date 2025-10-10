"""Login use case - 處理使用者登入邏輯。"""

from dataclasses import dataclass

from app.domain.entities.user import User


@dataclass
class LoginResult:
    """登入結果。"""

    access_token: str
    user: User


class LoginUseCase:
    """登入 Use Case - 主程式邏輯。"""

    def __init__(self, supabase_client):
        """初始化 LoginUseCase.

        Args:
            supabase_client: Supabase client 實例
        """
        self.supabase = supabase_client

    def execute(self, email: str, password: str) -> LoginResult:
        """執行登入邏輯.

        Args:
            email: 使用者 email
            password: 使用者密碼

        Returns:
            LoginResult: 登入結果（包含 access token 和使用者資訊）

        Raises:
            Exception: 當登入失敗時（例如密碼錯誤）
        """
        # 呼叫 Supabase Auth API
        response = self.supabase.auth.sign_in_with_password({"email": email, "password": password})

        # 建立 User entity
        user = User(id=response.user.id, email=response.user.email)

        # 返回結果
        return LoginResult(access_token=response.session.access_token, user=user)
