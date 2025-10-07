# 專案待辦清單

## 當前狀態

✅ 基礎 FastAPI 專案已建立
✅ Health check endpoint 已實作
✅ Docker 環境已設定
✅ 開發環境文件已完成（DEVELOPMENT.md）
✅ Git 敏感資料已清理

## 待辦事項

### Phase 0.5: API 基礎架構設計

- [ ] API 文件工具設定
  - [ ] 啟用 Swagger UI（FastAPI 內建）
  - [ ] 啟用 ReDoc（FastAPI 內建）
  - [ ] 研究並設定 Scalar（現代化文件介面）
- [ ] 錯誤處理架構（最終防線模式）
  - [ ] 建立自訂 Exception 類別（商業邏輯錯誤）
  - [ ] 實作全域 Exception Handler（FastAPI middleware）
  - [ ] 定義錯誤碼對照表（HTTP Status + 業務 code）
- [ ] API Response 格式標準化
  - [ ] 定義標準 JSON Response 格式
  - [ ] 建立 Response Model（Pydantic）
  - [ ] 實作 Response 包裝器
- [ ] 簡易認證機制（API Key）
  - [ ] 實作 API Key 驗證 middleware
  - [ ] 環境變數管理（.env）
  - [ ] TODO：未來升級為 Supabase JWT
- [ ] RESTful API Endpoints 設計
  - [ ] 撰寫 API_DESIGN.md（endpoint 規劃文件）
  - [ ] 定義資源命名規範
  - [ ] 設計 URL 結構與版本控制（/api/v1/）

### Phase 1: 環境建置與學習

- [ ] 學習 Supabase
  - [ ] 建立 Supabase 專案
  - [ ] 取得資料庫連線資訊
  - [ ] 測試基本 CRUD 操作
- [ ] 學習 Apify API
  - [ ] 取得 API Token
  - [ ] 測試 Amazon Product Details Actor
  - [ ] 確認資料格式
- [ ] 學習 OpenAI API
  - [ ] 測試 gpt-3.5-turbo 呼叫
  - [ ] 設計 structured prompt
- [ ] 選擇 Redis 服務
  - [ ] 比較 Redis Cloud / Upstash / 本地 Docker
  - [ ] 建立測試連線

### Phase 2: 架構設計文件

- [ ] 撰寫 ARCHITECTURE.md
- [ ] 撰寫 DATABASE_DESIGN.md
- [ ] 撰寫 API_DESIGN.md
- [ ] 繪製系統架構圖
- [ ] 更新 README.md 專案結構（待結構穩定後）

### Phase 3: 核心功能實作

待架構設計完成後再展開...

## 開發原則提醒

- ⚠️ 需要時才建立，避免過早優化
- ⚠️ 先實作 MVP，確認可行後再擴展
- ⚠️ 每個功能都要有明確的使用場景

## 參考文件

- [plan0.md](docs/plan0.md) - 初始規劃
- [plan1.md](docs/plan1.md) - 技術決策
