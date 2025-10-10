"""Login use case - 處理使用者登入邏輯。"""

from dataclasses import dataclass

from app.domain.entities.user import User
from app.use_cases.auth.ports import AuthRepository


@dataclass
class LoginResult:
    """登入結果。"""

    access_token: str
    user: User


class LoginUseCase:
    """登入 Use Case - 主程式邏輯。"""

    def __init__(self, auth_repo: AuthRepository):
        """初始化 LoginUseCase.

        Args:
            auth_repo: Auth Repository 實例（依賴抽象）
        """
        self.auth_repo = auth_repo

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
        # 透過 Repository 執行登入
        access_token, user = self.auth_repo.login(email, password)

        # 返回結果
        return LoginResult(access_token=access_token, user=user)
