"""Auth Repository 抽象介面（Ports）。"""

from abc import ABC, abstractmethod

from app.domain.entities.user import User


class AuthRepository(ABC):
    """認證 Repository 介面。"""

    @abstractmethod
    def signup(self, email: str, password: str) -> User:
        """註冊新使用者。

        Args:
            email: 使用者 email
            password: 使用者密碼

        Returns:
            User: 建立的使用者

        Raises:
            Exception: 當 email 已存在時
        """
        pass

    @abstractmethod
    def login(self, email: str, password: str) -> tuple[str, User]:
        """使用者登入。

        Args:
            email: 使用者 email
            password: 使用者密碼

        Returns:
            tuple[str, User]: (access_token, user)

        Raises:
            Exception: 當憑證無效時
        """
        pass
