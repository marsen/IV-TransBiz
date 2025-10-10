# 專案待辦清單

## 當前狀態

✅ 基礎 FastAPI 專案已建立
✅ Health check endpoint 已實作
✅ Docker 環境已設定
✅ 開發環境文件已完成（DEVELOPMENT.md）
✅ Git 敏感資料已清理

## 當前任務（2025-10-10）

### 🚧 Story 4.1: 使用者認證（P0 - MVP 必須）

**測試策略**: 只寫 Use Case Layer 的單元測試，Adapter Layer 不寫測試（用 Scalar 手動測試）

**Phase 1: Domain & Use Case Layer (TDD)** - ✅ 已完成

- [x] User Entity 實作與測試
- [x] SignupUseCase 單元測試 (RED)
- [x] SignupUseCase 實作 (GREEN)
- [x] LoginUseCase 單元測試 (RED)
- [x] LoginUseCase 實作 (GREEN)

**Phase 1.5: Repository Pattern 重構** - ✅ 已完成

- [x] 建立 AuthRepository 抽象介面 (ports.py)
- [x] 實作 SupabaseAuthRepository
- [x] 重構測試改為 mock Repository (RED)
- [x] 重構 Use Cases 使用 Repository (GREEN)

**Phase 2: Adapter Layer (API Endpoints)** - 🚧 進行中

- [x] 建立 auth schemas (SignupRequest/Response, LoginRequest/Response)
- [ ] 建立 auth router (`/api/v1/auth/signup` & `/login`)
- [ ] 註冊 router 到 main.py

**Phase 3: 手動測試** - ⏸️ 待開始

- [ ] 透過 Scalar docs 測試 signup endpoint
- [ ] 透過 Scalar docs 測試 login endpoint
- [ ] 驗證回應格式正確

**Supabase 設定**:

- [x] 設定 Supabase 連線與環境變數
- [x] 實作 fail-fast 驗證

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
