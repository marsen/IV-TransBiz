"""Supabase Auth Repository 實作。"""

from supabase import Client

from app.domain.entities.user import User
from app.use_cases.auth.ports import AuthRepository


class SupabaseAuthRepository(AuthRepository):
    """使用 Supabase 的 Auth Repository 實作。"""

    def __init__(self, supabase_client: Client):
        """初始化 Repository.

        Args:
            supabase_client: Supabase client 實例
        """
        self.supabase = supabase_client

    def signup(self, email: str, password: str) -> User:
        """註冊新使用者（實作）。

        Args:
            email: 使用者 email
            password: 使用者密碼

        Returns:
            User: 建立的使用者

        Raises:
            Exception: 當 email 已存在時
        """
        response = self.supabase.auth.sign_up({"email": email, "password": password})
        return User(id=response.user.id, email=response.user.email)

    def login(self, email: str, password: str) -> tuple[str, User]:
        """使用者登入（實作）。

        Args:
            email: 使用者 email
            password: 使用者密碼

        Returns:
            tuple[str, User]: (access_token, user)

        Raises:
            Exception: 當憑證無效時
        """
        response = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = User(id=response.user.id, email=response.user.email)
        return (response.session.access_token, user)
