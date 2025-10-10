"""Supabase Database Repository 實作。"""

from supabase import Client

from app.use_cases.health.ports import DatabaseRepository


class SupabaseDatabaseRepository(DatabaseRepository):
    """使用 Supabase 的 Database Repository 實作。"""

    def __init__(self, supabase_client: Client):
        """初始化 Repository.

        Args:
            supabase_client: Supabase client 實例
        """
        self.supabase = supabase_client

    def check_connection(self) -> str:
        """檢查 Supabase 連線狀態（實作）。

        Returns:
            str: "connected" 或錯誤訊息
        """
        try:
            # 測試 Supabase 連線
            self.supabase.auth.get_session()
            return "connected"
        except Exception as e:
            return f"error: {str(e)}"
