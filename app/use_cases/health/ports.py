"""Health Check Repository 抽象介面（Ports）- 從測試驅動出來。"""

from abc import ABC, abstractmethod


class DatabaseRepository(ABC):
    """資料庫連線檢查 Repository 介面。"""

    @abstractmethod
    def check_connection(self) -> str:
        """檢查資料庫連線狀態。

        Returns:
            str: 連線狀態訊息（"connected" 或錯誤訊息）
        """
        pass
