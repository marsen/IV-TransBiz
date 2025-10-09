# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

Amazon 產品監控與優化工具 - 一個 7 天的測試專案，目標是建立能夠追蹤 Amazon 產品表現、分析競爭對手並提供優化建議的系統。

**重要背景**：這是一個測試任務，**系統架構設計（50%）** 比功能實作（40%）更重要。重點是展現可擴展、可維護的系統設計能力。

## 開發指令

### 本地開發（使用 uv）

```bash
# 同步依賴（自動建立虛擬環境）
uv sync

# 啟動服務（支援 hot reload）
uv run uvicorn app.main:app --reload

# 安裝開發依賴
uv sync --extra dev
```

### Docker 開發

```bash
# 啟動服務
docker-compose up

# 依賴變更後重新建置
docker-compose up --build
```

### 程式碼品質檢查

```bash
# Ruff 程式碼檢查
uv run ruff check .

# 自動修正問題
uv run ruff check --fix .

# 格式化程式碼
uv run ruff format .

# 執行測試
uv run pytest
```

### Pre-commit Hooks

Pre-commit hooks 已設定（`.pre-commit-config.yaml`），會在 commit 時自動執行：

- Ruff linting 與自動修正
- Ruff 格式化
- Markdownlint 文件檢查

## 專案架構

### 目前狀態（Phase 0：基礎建置完成）

- ✅ FastAPI 應用程式初始化，含 health check
- ✅ Docker 環境設定完成
- ✅ 套件管理已遷移至 `uv` 使用 `pyproject.toml`
- ✅ Ruff linting 設定完成
- ✅ 靜態檔案服務（favicon）

### 專案結構

```text
app/
├── main.py          # FastAPI 應用程式進入點
└── static/          # 靜態資源（favicon 等）

docs/
├── Issues.md        # 測試案例需求（參考文件）
├── plan0.md         # 初始規劃（詳細架構提案）
├── plan1.md         # 技術決策與實作計劃
└── TODO.md          # 當前階段待辦清單
```

### 規劃中的架構（來自 docs/plan1.md）

系統將採用以下模組化設計：

```text
FastAPI Application (Uvicorn + ASGI)
├── Service Layer
│   ├── ProductService      # 產品追蹤邏輯
│   ├── CompetitorService   # 競品分析邏輯
│   ├── ListingService      # 優化建議生成
│   └── AuthService         # Supabase 認證
├── Celery Task Queue
│   ├── Apify 爬蟲任務
│   ├── OpenAI 分析任務
│   ├── 通知任務
│   └── Celery Beat（排程器）
└── External Services
    ├── Apify API（資料爬取）
    ├── OpenAI API（優化建議）
    ├── PostgreSQL（Supabase）
    └── Redis（快取 + broker）
```

## 開發原則（必須遵守）

來自 README.md - 這些是專案特定規則：

1. **過早優化是萬惡之源** - Donald Knuth
2. **需要時才建立** - 避免過度設計
3. **先列 TODO，後動手**：所有工作需先寫入 `docs/TODO.md` 並排序
4. **Commit 遵循 Conventional Commits**：格式為 `<type>: <description>`
5. **Fail-Fast 原則**：應用程式啟動時檢查必要環境變數，缺少時立即終止（不使用預設值）

### Commit 類型

- `feat`: 新功能
- `fix`: 修復 bug
- `docs`: 文件變更
- `style`: 格式調整（不影響程式碼運行）
- `refactor`: 重構（不是新功能也不是修 bug）
- `test`: 測試相關
- `chore`: 建構工具或輔助工具變更

## 關鍵技術決策（來自 docs/plan1.md）

### 技術棧（已確認）

- **後端**：Python + FastAPI（使用 asyncio）
- **資料庫**：Supabase（PostgreSQL）
- **快取**：Redis（服務選擇待定）
- **任務佇列**：Celery + Redis broker
- **資料爬取**：Apify API（Amazon Product Details、Amazon Reviews）
- **AI/LLM**：OpenAI API（優先使用 gpt-3.5-turbo 以控制成本）
- **部署**：Docker + Docker Compose

### 核心資料表（已規劃）

1. `users` - 使用者帳戶
2. `products` - 追蹤的產品主檔
3. `product_snapshots` - 時序資料（價格、BSR、評分等）
4. `competitors` - 競品關聯表
5. `optimization_suggestions` - 優化建議記錄
6. `notifications` - 異常通知記錄
7. `scraping_jobs` - 爬蟲任務狀態追蹤

### 快取策略（已規劃）

| 資料類型 | TTL | 理由 |
|---------|-----|------|
| 產品基本資訊 | 24h | 變動頻率低 |
| 產品快照資料 | 48h | 每日更新一次 |
| 競品分析報告 | 6h | 需較即時資料 |
| LLM 優化建議 | 24h | 成本考量 |

## 當前階段：Phase 1（環境建置與學習）

根據 `docs/TODO.md`，下一步需要：

1. 學習並設定 Supabase（建立專案、取得連線資訊、測試 CRUD）
2. 學習並測試 Apify API（取得 token、測試 Amazon Product Details Actor）
3. 學習並測試 OpenAI API（測試 gpt-3.5-turbo、設計 structured prompt）
4. 選擇 Redis 服務（比較 Redis Cloud / Upstash / 本地 Docker）

**Phase 2** 將進行架構設計文件撰寫（ARCHITECTURE.md、DATABASE_DESIGN.md、API_DESIGN.md）。

**Phase 3** 將進行核心功能實作（需從測試需求中選擇 2 項功能）。

## 測試需求背景

來自 `docs/Issues.md`：

- **第一部分（50%）**：系統架構設計 - 必須完成
- **第二部分（40%）**：核心功能實作 - 從以下選擇 2 項：
  1. 產品資料追蹤系統（支援 1000+ 產品、追蹤價格/BSR/評分）
  2. 競品分析引擎（比較 3-5 個競品）
  3. Listing 優化建議生成器（使用 OpenAI API）

**關鍵要求**：所有資料必須是來自 Apify 的真實即時資料 - 不接受 mock data。

## 重要注意事項

- **架構優先**：在實作前先完成架構設計文件
- **僅使用真實資料**：必須使用 Apify API 取得真實 Amazon 產品資料
- **成本意識**：使用 gpt-3.5-turbo 而非 GPT-4，對 LLM 建議實作 24h 快取
- **Demo 要求**：需準備 5-10 分鐘的 demo 影片展示真實資料
- **安全性**：絕不將 API keys 提交至 Git - .env 另外提供
- **測試覆蓋率**：核心邏輯目標達到 70%+ 測試覆蓋率
