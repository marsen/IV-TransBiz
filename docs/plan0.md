# 前期計劃書 - Amazon 產品監控與優化工具

## 專案概述

**目標**：為 Amazon 賣家設計並實作一個產品監控與優化工具，能夠追蹤產品表現、分析競爭對手，並提供優化建議。

**時間限制**：7天
**評分重點**：系統架構設計 > 功能實作

---

## 一、系統架構設計（必須完成，50%）

### 1.1 技術棧選擇

**後端框架**

- **建議**：Node.js + Express.js 或 Python + FastAPI
  - Node.js：與前端技術棧統一，適合高並發 I/O 操作
  - Python：生態系豐富（Celery、pandas），適合資料處理

**資料庫**

- **主資料庫**：Supabase (PostgreSQL)
- **快取層**：Redis（需自行架設或使用雲端服務）
- **任務佇列**：Bull (Node.js) 或 Celery (Python)

**資料擷取**

- Apify API（使用現有 Actor 或自建）
- 建議使用：Amazon Product Details、Amazon Reviews

**AI/LLM**

- OpenAI API（GPT-4 或 GPT-3.5-turbo）

**部署**

- Docker + Docker Compose
- 考慮使用 Railway、Render 或 Fly.io 進行部署

---

### 1.2 核心模組設計

```text
┌─────────────────────────────────────────────────────┐
│                    API Gateway                       │
│              (Express/FastAPI + Auth)                │
└──────────────┬──────────────────────────────────────┘
               │
       ┌───────┴────────┬──────────────┬──────────────┐
       │                │              │              │
┌──────▼──────┐  ┌──────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
│  Product    │  │ Competitor  │ │ Listing   │ │ Scheduler │
│  Tracking   │  │  Analysis   │ │Optimization│ │  Service  │
└──────┬──────┘  └──────┬──────┘ └────┬──────┘ └────┬──────┘
       │                │              │              │
       └────────┬───────┴──────────────┴──────────────┘
                │
         ┌──────▼──────────────────────┐
         │     Task Queue (Bull/Celery)│
         │  - Data Fetching Jobs       │
         │  - Analysis Jobs            │
         │  - Notification Jobs        │
         └──────┬──────────────────────┘
                │
    ┌───────────┴────────────┬─────────────────┐
    │                        │                 │
┌───▼────────┐      ┌────────▼────────┐  ┌────▼──────┐
│ Apify API  │      │   PostgreSQL    │  │   Redis   │
│  Scraper   │      │   (Supabase)    │  │   Cache   │
└────────────┘      └─────────────────┘  └───────────┘
```

---

### 1.3 資料庫設計重點

**核心資料表**

1. `users` - 使用者帳戶
2. `products` - 追蹤的產品主檔
3. `product_snapshots` - 產品時序資料（價格、BSR、評分等）
4. `competitors` - 競品關聯表
5. `optimization_suggestions` - 優化建議記錄
6. `notifications` - 異常通知記錄
7. `scraping_jobs` - 爬蟲任務狀態追蹤

**索引策略**

- `product_snapshots`: `(product_id, created_at DESC)` - 時序查詢
- `products`: `(user_id, category)` - 多租戶查詢
- `competitors`: `(main_product_id)` - 競品查詢

**分區考量**

- `product_snapshots` 按月份分區（如資料量大）

---

### 1.4 API 設計架構

**認證機制**

- JWT Token 基礎認證
- 使用 Supabase Auth（簡化實作）

**Rate Limiting**

- 每 IP 每分鐘 60 requests
- 使用 Redis 儲存 counter

**核心 API 端點**（詳細規格見 API_DESIGN.md）

```text
POST   /api/auth/login
GET    /api/products
POST   /api/products
GET    /api/products/:id/history
POST   /api/competitors
GET    /api/competitors/:id/report
POST   /api/optimization/suggest
GET    /api/notifications
```

---

### 1.5 快取與佇列設計

**Redis 快取策略**

| 資料類型 | TTL | 理由 |
|---------|-----|------|
| 產品基本資訊 | 24h | 變動頻率低 |
| 產品快照資料 | 48h | 每日更新一次 |
| 競品分析報告 | 6h | 需較即時資料 |
| LLM 優化建議 | 24h | 成本考量 |

**任務佇列設計**

- **高優先級**：使用者手動觸發的即時分析
- **中優先級**：異常通知發送
- **低優先級**：每日排程的產品資料更新

**批次處理**

- 每日凌晨 2:00 執行產品資料更新
- 分批處理（每批 50 個產品），避免 API rate limit

---

### 1.6 監控與維運

**Log 架構**

- 使用 Winston (Node.js) 或 Loguru (Python)
- Log Levels: ERROR > WARN > INFO > DEBUG
- 關鍵 Log 點：
  - API 請求/回應
  - Apify API 呼叫結果
  - 資料庫查詢效能
  - 任務佇列執行狀態

**關鍵指標（SLA/SLO）**

- API 可用性：99.5%
- API 回應時間：P95 < 500ms
- 每日資料更新完成率：99%

**錯誤追蹤**

- Sentry 或 LogRocket（加分項）
- 關鍵錯誤即時告警（Email 或 Slack）

---

## 二、核心功能實作選擇（選 2 項，40%）

### 建議選擇

**方案 A（推薦）：完整監控 + 優化建議**

- ✅ 選項 1：產品資料追蹤系統
- ✅ 選項 3：Listing 優化建議生成器
- **理由**：展現完整的「監控 → 分析 → 建議」閉環，且技術多樣性高

**方案 B（進階）：深度競品分析**

- ✅ 選項 2：競品分析引擎
- ✅ 選項 3：Listing 優化建議生成器
- **理由**：展現平行資料處理與 LLM 整合能力

---

### 2.1 選項 1：產品資料追蹤系統（建議實作）

**實作重點**

1. **Apify 整合**
   - 選擇合適的 Actor（如 `apify/amazon-product-scraper`）
   - 實作 webhook 或輪詢機制接收結果

2. **排程機制**
   - 使用 node-cron 或 Celery Beat
   - 每日凌晨 2:00 觸發批次更新

3. **異常偵測**
   - 價格變動 > 10% → 發送通知
   - BSR 變動 > 30% → 發送通知
   - 實作簡易 Email 或 Console Log 通知

4. **資料視覺化**
   - 產品價格趨勢圖（Chart.js）
   - BSR 排名變化圖
   - 評分/評論數變化

---

### 2.2 選項 3：Listing 優化建議生成器（建議實作）

**實作重點**

1. **Structured Prompt 設計**

   ```javascript
   const prompt = `
   分析以下 Amazon 產品資料，提供優化建議：

   產品標題：${title}
   價格：$${price}
   BSR：${bsr}
   評分：${rating} (${reviewCount} reviews)
   競品價格範圍：$${minPrice} - $${maxPrice}

   請提供以下建議：
   1. 標題優化（包含高搜尋量關鍵字）
   2. 定價調整（基於競品分析）
   3. 產品描述改進
   4. 圖片建議

   每個建議需包含：
   - 具體改進內容
   - 理由說明
   - 優先級（高/中/低）
   - 預期影響

   以 JSON 格式回傳。
   `;
   ```

2. **建議快取**
   - 同一產品 24 小時內不重複生成
   - 使用 Redis 儲存結果

3. **A/B 測試架構（加分）**
   - 追蹤建議採用率
   - 比對實施前後的 BSR/轉換率變化

---

## 三、開發流程規劃

### Day 1-2：架構設計與文件撰寫

- [ ] 完成系統架構圖（draw.io）
- [ ] 撰寫 ARCHITECTURE.md
- [ ] 撰寫 API_DESIGN.md
- [ ] 撰寫 DATABASE_DESIGN.md
- [ ] 設計資料庫 Schema（Supabase）
- [ ] 建立專案架構與 Docker Compose

### Day 3-4：核心功能實作 - 產品追蹤

- [ ] 實作 Apify API 整合
- [ ] 實作產品資料 CRUD API
- [ ] 實作排程系統（每日更新）
- [ ] 實作異常偵測與通知
- [ ] Redis 快取整合

### Day 5：核心功能實作 - 優化建議

- [ ] 實作 OpenAI API 整合
- [ ] 設計 Structured Prompt
- [ ] 實作建議生成 API
- [ ] 實作建議快取機制

### Day 6：測試與文件

- [ ] 單元測試（目標 70% coverage）
- [ ] 整合測試（真實 Apify/OpenAI API）
- [ ] 撰寫 README.md
- [ ] 撰寫 DESIGN_DECISIONS.md
- [ ] 生成 Swagger/Postman API 文件

### Day 7：Demo 準備與影片錄製

- [ ] 準備 10-20 個同類別產品（如無線藍牙耳機）
- [ ] 執行完整資料抓取與分析流程
- [ ] 錄製 Demo 影片（5-10 分鐘）
- [ ] 整理 .env.example 與環境變數
- [ ] 最終檢查與提交

---

## 四、技術決策與風險

### 4.1 主要技術決策

| 決策點 | 選項 | 理由 |
|--------|------|------|
| 後端語言 | **Node.js** vs Python | Node.js 開發速度快，適合 API 密集型應用 |
| 任務佇列 | **Bull** vs Celery | Bull 與 Node.js 整合簡單，Redis 原生支援 |
| 前端框架 | **Next.js** vs 純 API | 若有前端需求，Next.js 可快速建立 Dashboard |
| Apify Actor | **公開 Actor** vs 自建 | 公開 Actor 節省開發時間，但需確認資料格式 |

### 4.2 風險識別與應對

**風險 1：Apify API Rate Limit**

- **應對**：實作請求佇列，控制並發數量（每秒最多 2 requests）
- **應對**：使用 Redis 快取，避免重複請求

**風險 2：OpenAI API 成本過高**

- **應對**：使用 GPT-3.5-turbo 而非 GPT-4
- **應對**：實作 24h 快取，相同產品不重複生成建議
- **應對**：限制 prompt token 數量（< 2000 tokens）

**風險 3：資料抓取不穩定**

- **應對**：實作重試機制（最多 3 次，exponential backoff）
- **應對**：記錄失敗任務，手動重試或告警

**風險 4：時間不足**

- **應對**：優先完成架構設計與文件（佔 50%）
- **應對**：功能實作聚焦在 MVP，加分項視時間決定

---

## 五、加分項目優先級

如時間充裕，建議依序實作：

1. **✅ 高優先**：Swagger API 文件自動生成
2. **✅ 高優先**：Docker Compose 一鍵啟動
3. **✅ 中優先**：簡易前端 Dashboard（顯示產品追蹤結果）
4. **⚠️ 低優先**：CI/CD（GitHub Actions）
5. **⚠️ 低優先**：Prometheus + Grafana 監控
6. **⚠️ 低優先**：API 安全加固（HTTPS、CORS、Helmet）

---

## 六、Demo 產品選擇建議

**推薦類別**：無線藍牙耳機

**選擇理由**

- 競爭激烈，價格與排名變化明顯
- 產品資訊豐富（功能、規格、評論多）
- 便於展示優化建議（如標題、定價、特色對比）

**建議選取產品**

- 1 個主產品（假設為賣家自己的產品）
- 5-10 個競品（不同價格區間）
- 5-10 個同類產品（用於追蹤系統展示）

**範例 ASIN**（可搜尋 Amazon 實際 ASIN）

- 主產品：B0CX23V8SY（假設）
- 競品 1：B09ZV3KV3N（高價位）
- 競品 2：B0B7T1VFW2（中價位）
- 競品 3：B0BFZ6YNFN（低價位）

---

## 七、交付清單檢查

### 文件交付

- [ ] ARCHITECTURE.md
- [ ] API_DESIGN.md
- [ ] DATABASE_DESIGN.md
- [ ] README.md
- [ ] DESIGN_DECISIONS.md
- [ ] 系統架構圖（PNG/PDF）
- [ ] ERD 圖或 SQL schema dump

### 程式碼交付

- [ ] 2 個核心功能完整實作
- [ ] 單元測試（70%+ coverage）
- [ ] Docker Compose 設定
- [ ] .env.example

### API 文件

- [ ] Swagger UI 或 Postman Collection

### Demo

- [ ] 5-10 分鐘影片
- [ ] 使用真實 Amazon 產品資料
- [ ] 展示系統架構與資料流

### 安全性

- [ ] .env 不上傳至 GitHub
- [ ] 提供 Supabase 讀取權限或建置腳本
- [ ] 壓縮 .env 透過 Email 提供

---

## 八、下一步行動

請確認以下問題後，我們再進入實作階段：

1. **後端框架選擇**：Node.js (Express) 或 Python (FastAPI)？
2. **功能選擇**：方案 A（產品追蹤 + 優化建議）或方案 B（競品分析 + 優化建議）？
3. **前端需求**：是否需要簡易 Dashboard，還是純 API？
4. **部署環境**：本地 Docker 還是雲端部署（Railway/Render）？
5. **時間分配**：是否同意 Day 1-2 專注於架構設計與文件？

確認後我們可以開始建立專案結構並實作！
