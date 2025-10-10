"""Signup use case - 處理使用者註冊邏輯。"""

from dataclasses import dataclass

from app.domain.entities.user import User
from app.use_cases.auth.ports import AuthRepository


@dataclass
class SignupResult:
    """註冊結果。"""

    user: User
    message: str


class SignupUseCase:
    """註冊 Use Case - 主程式邏輯。"""

    def __init__(self, auth_repo: AuthRepository):
        """初始化 SignupUseCase。

        Args:
            auth_repo: Auth Repository 實例（依賴抽象）
        """
        self.auth_repo = auth_repo

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
        # 透過 Repository 執行註冊
        user = self.auth_repo.signup(email, password)

        # 返回結果
        return SignupResult(user=user, message="User created successfully")
