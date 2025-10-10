# 專案待辦清單

## 當前狀態

✅ 基礎 FastAPI 專案已建立
✅ Health check endpoint 已實作
✅ Docker 環境已設定
✅ 開發環境文件已完成（DEVELOPMENT.md）
✅ Git 敏感資料已清理

## 當前任務（2025-10-09）

### 🚧 Story 4.1: 使用者認證（P0 - MVP 必須）

**Phase 1: 註冊功能 (Signup)** - 🚧 進行中

測試案例 (TDD - RED):

- [x] test_signup_success - 註冊成功 (201)
- [x] test_signup_email_already_exists - Email 已存在 (400)
- [ ] test_signup_invalid_email_format - 無效 email 格式 (422) 🔴 P0
- [ ] test_signup_missing_email - 缺少 email 欄位 (422) 🔴 P0
- [ ] test_signup_missing_password - 缺少 password 欄位 (422) 🔴 P0

實作任務 (TDD - GREEN):

- [ ] 建立 auth schemas (SignupRequest, SignupResponse)
- [ ] 建立 auth router (`/api/v1/auth/signup`)
- [ ] 註冊 router 到 main.py
- [ ] 驗證測試通過 (GREEN)

**Phase 2: 登入功能 (Login)** - ⏸️ 待開始

測試案例:

- [ ] test_login_success - 登入成功返回 JWT (200)
- [ ] test_login_invalid_password - 錯誤密碼 (401)

實作任務:

- [ ] 建立 login endpoint (`/api/v1/auth/login`)
- [ ] 驗證測試通過

**Phase 3: 認證中介層 (Auth Middleware)** - ⏸️ 待開始

測試案例:

- [ ] test_unauthorized_access - 未登入訪問受保護 API (401)

實作任務:

- [ ] 實作 get_current_user() dependency
- [ ] 為受保護 API 加上認證檢查
- [ ] 驗證測試通過

**Supabase 設定**:

- [x] 設定 Supabase 連線與環境變數

### 📝 Story 1.1: 新增追蹤產品（P0 - MVP 必須）

- [ ] 建立 products 資料表 schema
- [ ] 實作 Apify 爬蟲整合
- [ ] 實作 POST /api/v1/products endpoint

---

## 待辦事項（Phase 1 MVP）

### Story 1.2: 查看產品列表（P0）

- [ ] 實作 GET /api/v1/products endpoint
- [ ] 支援分頁與排序
- [ ] 顯示警報標記

### Story 2.1 + 2.2: 價格/BSR 變動警報（P0）

- [ ] 建立 change_alerts 資料表
- [ ] 實作價格變動檢測邏輯（>10%）
- [ ] 實作 BSR 變動檢測邏輯（>30%）
- [ ] 實作 LogNotifier

### Story 3.1: 每日自動更新（P0）

- [ ] 設定 Celery + Redis
- [ ] 實作 BatchUpdateSnapshotsUseCase
- [ ] 設定 Celery Beat 排程（每日 02:00）
- [ ] 並發更新實作（asyncio.gather）

---

## 已完成

### Phase 0: 基礎建置

✅ FastAPI 應用程式初始化
✅ Health check endpoint
✅ Docker 環境設定
✅ uv 套件管理設定
✅ Ruff linting 設定
✅ Scalar API 文件設定

### Phase 1 & 2: 架構設計

✅ 技術棧決策（docs/plan1.md）
✅ Clean Architecture 設計（docs/plan2.md）
✅ 產品追蹤系統設計（docs/plan3.md）
✅ User Stories 定義（docs/stories.md）
✅ 對話狀態記錄（docs/SESSION_STATE.md）

## 開發原則提醒

- ⚠️ 需要時才建立，避免過早優化
- ⚠️ 先實作 MVP，確認可行後再擴展
- ⚠️ 每個功能都要有明確的使用場景

## 參考文件

- [plan0.md](docs/plan0.md) - 初始規劃
- [plan1.md](docs/plan1.md) - 技術決策
