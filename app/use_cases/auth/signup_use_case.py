"""Signup use case - 處理使用者註冊邏輯。"""

from dataclasses import dataclass

from app.domain.entities.user import User


@dataclass
class SignupResult:
    """註冊結果。"""

    user: User
    message: str


class SignupUseCase:
    """註冊 Use Case - 主程式邏輯。"""

    def __init__(self, supabase_client):
        """初始化 SignupUseCase。

        Args:
            supabase_client: Supabase client 實例
        """
        self.supabase = supabase_client

    def execute(self, email: str, password: str) -> SignupResult:
        """執行註冊邏輯。

        Args:
            email: 使用者 email
            password: 使用者密碼

        Returns:
            SignupResult: 註冊結果（包含使用者資訊和訊息）

        Raises:
            Exception: 當註冊失敗時（例如 email 已存在）
        """
        # 呼叫 Supabase Auth API
        response = self.supabase.auth.sign_up({"email": email, "password": password})

        # 建立 User entity
        user = User(id=response.user.id, email=response.user.email)

        # 返回結果
        return SignupResult(user=user, message="User created successfully")
