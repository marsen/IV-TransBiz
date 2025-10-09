"""Application configuration with fail-fast validation."""

import os
import sys

from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


def get_required_env(key: str) -> str:
    """取得必要的環境變數，若缺少則立即終止程式。

    Args:
        key: 環境變數名稱

    Returns:
        環境變數值

    Raises:
        SystemExit: 當環境變數不存在或為空時
    """
    value = os.getenv(key)
    if not value:
        print(f"❌ 錯誤：缺少必要環境變數 {key}", file=sys.stderr)
        print(f"請在 .env 檔案中設定 {key}", file=sys.stderr)
        sys.exit(1)
    return value


# Supabase 設定
SUPABASE_URL = get_required_env("SUPABASE_URL")
SUPABASE_ANON_KEY = get_required_env("SUPABASE_ANON_KEY")
