# Plan 1 - 技術決策與實作計劃

基於 plan0.md 的討論，以下為確認的技術決策與待辦事項。

---

## 一、已確認的技術決策

### 1.1 技術棧選擇

#### 後端框架

- **✅ 確定使用**：Python + FastAPI
  - 使用 `asyncio` 處理異步操作
  - 生態系豐富（Celery、pandas、pydantic）
  - 適合資料處理與 AI 整合

#### 資料庫

- **✅ 主資料庫**：Supabase (PostgreSQL)
  - **待學習**：需要 Supabase 設定與使用指引
  - **待辦**：建立 Supabase 專案並取得連線資訊

#### 快取層

- **✅ 確定使用**：Redis
  - **待確認**：Redis 雲端服務選項
  - **建議選項**：
    1. **Redis Cloud** (官方，有免費 30MB 方案)
    2. **Upstash** (Serverless Redis，免費 10K requests/day)
    3. **Railway** (整合部署，Redis 月費約 $5)
    4. **本地 Docker** (開發測試用)

#### 任務佇列

- **✅ 確定使用**：Celery
  - 使用 Redis 作為 broker
  - Celery Beat 處理排程任務

#### 資料擷取

- **✅ 使用**：Apify API
  - **待學習**：Apify API 基礎使用指引
  - **說明**：`Amazon Product Details` 與 `Amazon Reviews` 是 Apify 平台上的公開 Actor（爬蟲）
    - **Amazon Product Details**：抓取產品基本資訊（標題、價格、BSR、圖片等）
    - **Amazon Reviews**：抓取產品評論資料
  - **待辦**：測試 Apify Actor 並確認資料格式

#### AI/LLM

- **✅ 使用**：OpenAI API
  - 已提供 API Key
  - **待學習**：OpenAI Python SDK 使用指引
  - **建議**：使用 `gpt-3.5-turbo` 控制成本

#### 部署

- **✅ 本地開發**：Docker + Docker Compose
  - **待辦**：建立 Dockerfile 與 docker-compose.yml
- **❓ 雲端部署**：非必要，但建議考慮
  - **選項**：Railway、Render、Fly.io
  - **評估**：Demo 可使用本地環境，雲端部署為加分項

---

### 1.2 核心模組設計（重新規劃）

基於 Python + FastAPI 技術棧，重新設計系統架構：

```text
┌─────────────────────────────────────────────────────┐
│              FastAPI Application                     │
│         (Uvicorn + ASGI + Async Routes)              │
└──────────────┬──────────────────────────────────────┘
               │
       ┌───────┴────────┬──────────────┬──────────────┐
       │                │              │              │
┌──────▼──────┐  ┌──────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
│  Product    │  │ Competitor  │ │ Listing   │ │   Auth    │
│  Service    │  │  Service    │ │  Service  │ │  Service  │
│             │  │             │ │           │ │(Supabase) │
└──────┬──────┘  └──────┬──────┘ └────┬──────┘ └───────────┘
       │                │              │
       └────────┬───────┴──────────────┘
                │
         ┌──────▼──────────────────────┐
         │   Celery Task Queue          │
         │   (Celery + Redis Broker)    │
         │  - Apify Scraping Tasks      │
         │  - OpenAI Analysis Tasks     │
         │  - Notification Tasks        │
         │  - Celery Beat (Scheduler)   │
         └──────┬──────────────────────┘
                │
    ┌───────────┴────────────┬─────────────────┐
    │                        │                 │
┌───▼────────┐      ┌────────▼────────┐  ┌────▼──────┐
│ Apify API  │      │   PostgreSQL    │  │   Redis   │
│            │      │   (Supabase)    │  │           │
│ - Product  │      │                 │  │  - Cache  │
│   Details  │      │  - SQLAlchemy   │  │  - Broker │
│ - Reviews  │      │  - Async Pool   │  │  - Result │
└────────────┘      └─────────────────┘  └───────────┘
```

**模組說明**：

1. **FastAPI Application**
   - 非同步 API 路由（async/await）
   - Pydantic 資料驗證
   - 自動生成 OpenAPI/Swagger 文件

2. **Service Layer**
   - `ProductService`: 產品追蹤邏輯
   - `CompetitorService`: 競品分析邏輯
   - `ListingService`: 優化建議生成
   - `AuthService`: Supabase 認證整合

3. **Celery Task Queue**
   - 異步任務處理
   - Celery Beat 定時任務
   - Redis 作為 broker 與 result backend

4. **External Services**
   - Apify API Client
   - OpenAI API Client
   - Supabase Client (PostgreSQL + Auth)

---

### 1.3 資料庫設計

**保留原計劃**，待後續討論細節。

核心資料表：

1. `users`
2. `products`
3. `product_snapshots`
4. `competitors`
5. `optimization_suggestions`
6. `notifications`
7. `scraping_jobs`

---

### 1.4 API 設計架構

**商業需求，列入待辦清單**。

核心 API 端點待設計：

- 認證 API
- 產品管理 API
- 競品分析 API
- 優化建議 API
- 通知 API

---

### 1.5 快取與佇列設計

**保留原計劃**，待後續討論細節。

---

### 1.6 監控與維運（Python 技術棧）

#### Log 架構

- **✅ 使用**：Python `logging` 模組或 `Loguru`
  - Log Levels: ERROR > WARNING > INFO > DEBUG
  - 結構化日誌（JSON format）
  - 關鍵 Log 點：
    - FastAPI 請求/回應（middleware）
    - Apify API 呼叫結果
    - 資料庫查詢效能（SQLAlchemy echo）
    - Celery 任務執行狀態

#### 關鍵指標（SLA/SLO）

- **待辦**：建立效能測試與壓測環境
  - API 可用性目標：99.5%
  - API 回應時間目標：P95 < 500ms
  - 每日資料更新完成率：99%
- **工具建議**：
  - `locust` 或 `pytest-benchmark` 進行壓測
  - 記錄測試結果於 `PERFORMANCE.md`

#### 錯誤追蹤

- **待辦**：整合錯誤追蹤工具
  - **選項 1**：Sentry（推薦，有免費方案）
  - **選項 2**：簡易日誌記錄（MVP 階段）
  - 關鍵錯誤告警機制（Email 或 Console）

---

## 二、待辦事項清單

### 學習與研究

- [ ] **Supabase 使用指引**
  - 建立專案、資料庫連線
  - Python 客戶端 (`supabase-py`) 使用
  - 認證機制整合
- [ ] **Apify API 指引**
  - 註冊與 API Token 取得
  - Actor 執行與結果取得
  - Webhook 與輪詢機制
- [ ] **OpenAI API 指引**
  - Python SDK (`openai`) 使用
  - Structured output 與 JSON mode
  - Token 計算與成本控制
- [ ] **Redis 雲端服務評估**
  - 比較 Redis Cloud、Upstash、Railway
  - 選擇適合的免費/低成本方案

### 架構與設計

- [ ] **完成系統架構圖**（draw.io）
- [ ] **撰寫 ARCHITECTURE.md**
- [ ] **撰寫 DATABASE_DESIGN.md**
- [ ] **撰寫 API_DESIGN.md**（商業需求規格）
- [ ] **設計資料庫 Schema**（Supabase）

### 開發環境

- [ ] **建立專案結構**

  ```text
  transbiz/
  ├── app/
  │   ├── api/          # FastAPI routes
  │   ├── services/     # Business logic
  │   ├── models/       # SQLAlchemy models
  │   ├── schemas/      # Pydantic schemas
  │   ├── tasks/        # Celery tasks
  │   └── core/         # Config, dependencies
  ├── tests/
  ├── docker-compose.yml
  ├── Dockerfile
  ├── requirements.txt
  └── .env.example
  ```

- [ ] **Docker Compose 設定**
  - FastAPI service
  - PostgreSQL (或使用雲端 Supabase)
  - Redis
  - Celery worker
  - Celery beat
- [ ] **依賴套件清單**（requirements.txt）

  ```text
  fastapi
  uvicorn[standard]
  sqlalchemy
  asyncpg
  supabase
  redis
  celery
  apify-client
  openai
  pydantic
  pydantic-settings
  python-dotenv
  ```

### 核心功能實作

- [ ] **Apify 整合測試**
  - 測試 Amazon Product Details Actor
  - 確認資料格式與欄位
- [ ] **OpenAI 整合測試**
  - 測試 GPT-3.5-turbo API
  - 設計 Structured Prompt
- [ ] **Supabase 連線測試**
  - 建立資料表
  - 測試 CRUD 操作

### 效能與監控

- [ ] **建立壓測環境**
  - 使用 `locust` 或 `pytest-benchmark`
  - 測試 API 回應時間與並發處理
  - 記錄於 `PERFORMANCE.md`
- [ ] **整合錯誤追蹤**
  - 評估 Sentry 或自建日誌系統
  - 實作關鍵錯誤告警

### 部署環境

- [ ] **本地 Docker 部署**
  - 確保 `docker-compose up` 一鍵啟動
- [ ] **（可選）雲端部署**
  - 評估 Railway/Render/Fly.io
  - 設定環境變數與 secrets

---

## 三、技術指引需求

請依序提供以下技術指引：

### 3.1 Supabase 快速入門

- [ ] 如何建立 Supabase 專案
- [ ] 如何取得資料庫連線資訊（PostgreSQL URL）
- [ ] `supabase-py` 客戶端基礎使用
- [ ] Supabase Auth 整合（JWT Token）
- [ ] 如何建立資料表與執行 SQL

### 3.2 Apify API 快速入門

- [ ] 如何取得 API Token
- [ ] 如何執行 Amazon Product Details Actor
- [ ] 如何取得執行結果（輪詢或 Webhook）
- [ ] 資料格式範例與欄位說明
- [ ] Rate limit 與計費說明

### 3.3 OpenAI API 快速入門

- [ ] `openai` Python SDK 安裝與使用
- [ ] 如何呼叫 `gpt-3.5-turbo` 模型
- [ ] Structured output 與 JSON mode 使用
- [ ] Token 計算與成本控制
- [ ] Error handling 與重試機制

### 3.4 Redis 雲端服務選擇

- [ ] Redis Cloud vs Upstash vs Railway 比較
- [ ] 免費方案限制與選擇建議
- [ ] 連線設定與測試

---

## 四、未決事項

以下問題待後續討論：

1. **功能選擇**：方案 A（產品追蹤 + 優化建議）或方案 B（競品分析 + 優化建議）？
2. **前端需求**：是否需要簡易 Dashboard（如使用 Streamlit 或純 HTML/JS）？
3. **部署策略**：Demo 是否需要雲端部署，或本地 Docker 即可？
4. **測試覆蓋率**：如何達到 70% 單元測試覆蓋率（測試框架：pytest）？
5. **時間分配**：是否同意 Day 1-2 完成架構設計與環境建置？

---

## 五、下一步行動

建議按以下順序進行：

1. **✅ 立即行動**：提供 Supabase、Apify、OpenAI 技術指引
2. **Day 1**：建立專案結構、Docker 環境、測試外部服務連線
3. **Day 2**：完成架構文件與資料庫設計
4. **Day 3-5**：實作核心功能
5. **Day 6-7**：測試、文件、Demo

**請確認是否需要我先提供技術指引，或直接開始建立專案結構？**
