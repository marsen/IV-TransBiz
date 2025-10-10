"""Supabase client singleton - 供所有 repositories 共用。"""

from supabase import Client, create_client

from app.config import SUPABASE_ANON_KEY, SUPABASE_URL

# Module-level singleton
_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """取得 Supabase client singleton.

    Returns:
        Client: Supabase client 實例
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _supabase_client
