# User Stories - Amazon 產品監控工具

## 主要角色（Persona）

### Amazon 賣家（Seller）

**角色描述**：

- **姓名**：Sarah
- **身份**：在 Amazon 美國站賣藍牙耳機的小賣家
- **規模**：有 15 個 SKU（產品）在銷售
- **痛點**：
  - 每天手動檢查產品價格和排名太累
  - 競爭對手突然降價，她晚了 2 天才發現，銷量掉了 40%
  - 不知道自己的 BSR 排名什麼時候掉了
- **目標**：自動化監控所有產品，第一時間發現異常變化

---

## Epic 1：追蹤管理 📝

### Story 1.1：新增追蹤產品 📝

**狀態**：📝 待辦
**優先級**：🔴 P0（MVP 必須）
**預估工時**：4 小時

**User Story**：

```gherkin
As a Amazon 賣家
I want to 透過輸入 ASIN 新增要追蹤的產品
So that 系統可以幫我自動監控這個產品的表現
```

**驗收標準（Acceptance Criteria）**：

- [ ] 可以輸入 ASIN（例如 B08XYZ1234）
- [ ] 系統自動從 Amazon 抓取產品基本資訊（標題、類別、當前價格）
- [ ] 新增成功後顯示在我的追蹤列表
- [ ] 如果 ASIN 無效，顯示錯誤訊息
- [ ] 同一個 ASIN 不能重複新增
- [ ] 只有登入使用者才能新增產品

**使用流程**：

```text
1. Sarah 登入系統
2. 點擊「新增產品」按鈕
3. 輸入她的新產品 ASIN: B08ABC1234
4. 系統呼叫 Apify 爬蟲，抓取產品資料
5. 顯示：「✅ 成功追蹤：Bluetooth Earbuds Pro - $29.99」
6. 產品出現在「我的追蹤列表」
```

**技術實作**：

- API: `POST /api/v1/products`
- Request Body: `{ "asin": "B08ABC1234" }`
- Use Case: `TrackProductUseCase`
- 呼叫 Apify Actor: `curious_coder/amazon-scraper`

**測試案例**：

- 正常流程：輸入有效 ASIN
- 異常流程：輸入無效 ASIN（應回傳 400）
- 異常流程：ASIN 已存在（應回傳 409）
- 異常流程：未登入（應回傳 401）

---

### Story 1.2：查看追蹤產品列表 📝

**狀態**：📝 待辦
**優先級**：🔴 P0（MVP 必須）
**預估工時**：3 小時

**User Story**：

```gherkin
As a Amazon 賣家
I want to 看到我所有正在追蹤的產品及其當前狀態
So that 我可以快速了解所有產品的概況
```

**驗收標準**：

- [ ] 顯示產品列表（ASIN、標題、當前價格、BSR、最後更新時間）
- [ ] 只顯示我自己追蹤的產品（不是其他賣家的）
- [ ] 可以排序（按價格、BSR、更新時間）
- [ ] 顯示警報標記（如果有異常變化）
- [ ] 支援分頁（每頁 20 筆）

**畫面示意**：

```text
我的追蹤產品 (15 個)

┌─────────────┬──────────────────────────────┬──────────┬──────────┬────────────┐
│ 狀態        │ 產品                         │ 價格     │ BSR      │ 更新時間   │
├─────────────┼──────────────────────────────┼──────────┼──────────┼────────────┤
│ 🔴 警報     │ B08ABC1234                   │ $24.99   │ #200     │ 2 小時前   │
│             │ Bluetooth Earbuds Pro        │ ↓16.7%   │ ↓75%     │            │
├─────────────┼──────────────────────────────┼──────────┼──────────┼────────────┤
│ 🟢 正常     │ B07DEF5678                   │ $49.99   │ #45      │ 2 小時前   │
│             │ Wireless Headphones Ultra    │          │          │            │
└─────────────┴──────────────────────────────┴──────────┴──────────┴────────────┘
```

**技術實作**：

- API: `GET /api/v1/products?page=1&limit=20&sort_by=price&order=desc`
- Response: 產品列表 + 分頁資訊
- 查詢條件：`WHERE user_id = current_user AND is_active = true`
- Join: 最新的 snapshot 資料

**測試案例**：

- 正常流程：查看產品列表
- 邊界條件：無產品時顯示空列表
- 邊界條件：分頁邊界測試
- 權限：只能看到自己的產品

---

### Story 1.3：查看產品歷史趨勢 📝

**狀態**：📝 待辦
**優先級**：🟡 P1（重要但非必須）
**預估工時**：5 小時

**User Story**：

```gherkin
As a Amazon 賣家
I want to 查看某個產品過去 30 天的價格和 BSR 趨勢圖
So that 我可以分析產品表現的變化模式
```

**驗收標準**：

- [ ] 顯示過去 30 天的歷史資料列表
- [ ] 包含每日的價格、BSR、評分、評論數
- [ ] 可以切換時間範圍（7 天、30 天、90 天）
- [ ] 顯示變化趨勢（上升/下降/持平）
- [ ] （選配）折線圖視覺化

**資料示意**：

```text
產品歷史：Bluetooth Earbuds Pro (B08ABC1234)

時間範圍：[7天] [30天] [90天]

┌────────────┬──────────┬──────────┬────────┬────────────┐
│ 日期       │ 價格     │ BSR      │ 評分   │ 評論數     │
├────────────┼──────────┼──────────┼────────┼────────────┤
│ 2025-10-08 │ $24.99   │ #200     │ 4.5★   │ 1,350      │
│ 2025-10-07 │ $29.99   │ #50      │ 4.5★   │ 1,200      │
│ 2025-10-06 │ $29.99   │ #48      │ 4.5★   │ 1,180      │
│ ...        │ ...      │ ...      │ ...    │ ...        │
└────────────┴──────────┴──────────┴────────┴────────────┘

趨勢摘要：
- 價格：↓ 16.7%（過去 1 天）
- BSR：↓ 300%（過去 1 天）⚠️
- 評論數：+150（過去 7 天）
```

**技術實作**：

- API: `GET /api/v1/products/{id}/history?days=30`
- Use Case: `GetProductHistoryUseCase`
- 查詢：`product_snapshots` 表，按日期排序
- 回傳：JSON 陣列（適合前端繪製圖表）

**測試案例**：

- 正常流程：查詢有資料的產品
- 邊界條件：新產品（只有 1 天資料）
- 邊界條件：查詢超過實際資料天數
- 權限：只能查詢自己的產品

---

### Story 1.4：查看產品詳細資訊 📝

**狀態**：📝 待辦
**優先級**：🟡 P1（重要但非必須）
**預估工時**：2 小時

**User Story**：

```gherkin
As a Amazon 賣家
I want to 查看某個產品的完整詳細資訊
So that 我可以了解該產品的最新狀態和所有追蹤指標
```

**驗收標準**：

- [ ] 顯示產品基本資訊（ASIN、標題、類別）
- [ ] 顯示最新快照資料（價格、BSR、評分、評論數、Buy Box 價格）
- [ ] 顯示上次更新時間
- [ ] 顯示追蹤開始日期
- [ ] 提供「立即更新」按鈕（手動觸發爬蟲）

**技術實作**：

- API: `GET /api/v1/products/{id}`
- 回傳：產品資訊 + 最新 snapshot

---

### Story 1.5：手動更新產品資料 📝

**狀態**：📝 待辦
**優先級**：🟢 P2（Nice to have）
**預估工時**：3 小時

**User Story**：

```gherkin
As a Amazon 賣家
I want to 手動觸發某個產品的資料更新
So that 我不用等到每日自動更新時間，就能看到最新資料
```

**驗收標準**：

- [ ] 點擊「立即更新」按鈕觸發爬蟲
- [ ] 顯示更新進度（載入中）
- [ ] 更新完成後顯示最新資料
- [ ] 如果爬蟲失敗，顯示錯誤訊息
- [ ] 有 rate limit 保護（同一產品 1 小時內只能手動更新 3 次）

**技術實作**：

- API: `POST /api/v1/products/{id}/snapshots`
- Use Case: `UpdateProductSnapshotUseCase`
- Rate Limit: Redis 計數器（key: `manual_update:{product_id}`）

---

### Story 1.6：停止追蹤產品 📝

**狀態**：📝 待辦
**優先級**：🟡 P1（重要但非必須）
**預估工時**：2 小時

**User Story**：

```gherkin
As a Amazon 賣家
I want to 移除不再銷售的產品
So that 我可以節省系統資源和 API 成本
```

**驗收標準**：

- [ ] 點擊「停止追蹤」按鈕
- [ ] 確認對話框（避免誤刪）
- [ ] 產品從列表中移除（軟刪除，`is_active = false`）
- [ ] 歷史資料保留（不刪除 snapshots）
- [ ] 每日自動更新時跳過此產品

**技術實作**：

- API: `DELETE /api/v1/products/{id}`
- 實作：軟刪除（`UPDATE products SET is_active = false WHERE id = ?`）
- 權限檢查：只能刪除自己的產品

---

## Epic 2：異常通知 📝

### Story 2.1：自動生成價格變動警報 📝

**狀態**：📝 待辦
**優先級**：🔴 P0（MVP 必須）
**預估工時**：4 小時

**User Story**：

```gherkin
As a Amazon 賣家
I want to 當產品價格變動超過 10% 時自動生成警報
So that 我可以快速反應，調整我的定價策略
```

**驗收標準**：

- [ ] 每日自動更新時，比較新舊快照的價格
- [ ] 如果變化 > 10%，自動生成警報記錄（`change_alerts` 表）
- [ ] 警報包含：產品 ID、舊價格、新價格、變化百分比、觸發時間
- [ ] 警報狀態初始為「未讀」（`notified = false`）

**業務邏輯**：

```python
# 在 UpdateProductSnapshotUseCase 中實作
if abs(price_change_percentage) >= 10:
    create_alert(
        product_id=product_id,
        alert_type="PRICE_CHANGE",
        old_value=old_price,
        new_value=new_price,
        change_percentage=price_change_percentage
    )
    notifier.send_price_alert(...)
```

**技術實作**：

- Use Case: `UpdateProductSnapshotUseCase._check_and_notify_changes()`
- 通知方式：`LogNotifier`（初期）/ `EmailNotifier`（未來）
- 資料表：`change_alerts`

**測試案例**：

- 價格變化 +15% → 生成警報
- 價格變化 -12% → 生成警報
- 價格變化 +5% → 不生成警報
- 價格從 null → $29.99 → 不生成警報（首次記錄）

---

### Story 2.2：自動生成 BSR 變動警報 📝

**狀態**：📝 待辦
**優先級**：🔴 P0（MVP 必須）
**預估工時**：3 小時

**User Story**：

```gherkin
As a Amazon 賣家
I want to 當產品的小類別 BSR 排名變動超過 30% 時自動生成警報
So that 我可以了解產品競爭力是否下降，並採取行動
```

**驗收標準**：

- [ ] 比較小類別 BSR（`bsr_sub`）的變化
- [ ] 如果變化 > 30%，自動生成警報
- [ ] 警報包含：產品 ID、舊排名、新排名、變化百分比
- [ ] 警報類型：`BSR_CHANGE`

**業務邏輯**：

```python
# BSR 變化計算（注意：排名變大 = 表現變差）
bsr_change_percentage = (new_bsr - old_bsr) / old_bsr * 100

# 例如：從 #50 → #200
# (200 - 50) / 50 * 100 = 300%（變差了）
```

**技術實作**：

- Use Case: `UpdateProductSnapshotUseCase._check_and_notify_changes()`
- 通知方式：`LogNotifier`
- 資料表：`change_alerts`

---

### Story 2.3：查看警報列表 📝

**狀態**：📝 待辦
**優先級**：🟡 P1（重要但非必須）
**預估工時**：3 小時

**User Story**：

```gherkin
As a Amazon 賣家
I want to 查看所有產品的警報記錄
So that 我可以了解近期哪些產品有異常變化
```

**驗收標準**：

- [ ] 顯示所有警報（價格警報 + BSR 警報）
- [ ] 按時間倒序排列（最新的在上面）
- [ ] 區分「未讀」和「已讀」警報
- [ ] 顯示警報類型圖示（⚠️ 價格 / 📊 BSR）
- [ ] 支援篩選（只看未讀、只看價格警報、只看 BSR 警報）

**畫面示意**：

```text
警報中心 (5 個未讀)

[全部] [未讀] [價格警報] [BSR 警報]

┌────────────┬──────────────────────────────────────────────────┐
│ 2025-10-08 │ ⚠️ 價格警報：Bluetooth Earbuds Pro (B08ABC1234)   │
│ 02:15      │ 降價 16.7%（$29.99 → $24.99）                    │
│            │ [查看詳情] [標記已讀]                             │
├────────────┼──────────────────────────────────────────────────┤
│ 2025-10-08 │ 📊 BSR 警報：Bluetooth Earbuds Pro (B08ABC1234)   │
│ 02:15      │ 排名下跌 300%（#50 → #200）                      │
│            │ [查看詳情] [標記已讀]                             │
└────────────┴──────────────────────────────────────────────────┘
```

**技術實作**：

- API: `GET /api/v1/alerts?status=unread&type=PRICE_CHANGE`
- 查詢：`change_alerts` JOIN `products`
- 過濾：只顯示當前使用者的產品警報

---

### Story 2.4：標記警報為已讀 📝

**狀態**：📝 待辦
**優先級**：🟢 P2（Nice to have）
**預估工時**：1 小時

**User Story**：

```gherkin
As a Amazon 賣家
I want to 將警報標記為已讀
So that 我可以專注在未處理的警報上
```

**驗收標準**：

- [ ] 點擊「標記已讀」按鈕
- [ ] 警報從「未讀」列表移除
- [ ] 資料庫更新：`UPDATE change_alerts SET notified = true WHERE id = ?`

**技術實作**：

- API: `PATCH /api/v1/alerts/{id}`
- Request Body: `{ "notified": true }`

---

## Epic 3：背景任務 📝

### Story 3.1：每日自動更新所有產品 📝

**狀態**：📝 待辦
**優先級**：🔴 P0（MVP 必須）
**預估工時**：6 小時

**User Story**：

```gherkin
As a 系統管理員
I want to 每天凌晨 2:00 自動更新所有產品的快照資料
So that 使用者早上登入時可以看到最新資料
```

**驗收標準**：

- [ ] Celery Beat 排程任務：每天凌晨 2:00 執行
- [ ] 查詢所有 `is_active = true` 的產品
- [ ] 並發更新所有產品（使用 `asyncio.gather`）
- [ ] 記錄執行結果（成功數量、失敗數量、錯誤清單）
- [ ] 自動生成警報（價格/BSR 變化超過門檻）
- [ ] 發送通知（LogNotifier）

**業務邏輯**：

```python
# Celery Task
@celery_app.task(name="daily_update_snapshots")
async def daily_update_snapshots():
    use_case = BatchUpdateSnapshotsUseCase(...)
    results = await use_case.execute()

    # 記錄結果
    logger.info(f"Daily update completed: {results}")
    # results = {
    #     "total": 1000,
    #     "success": 980,
    #     "failed": 20,
    #     "errors": [...]
    # }
```

**技術實作**：

- Celery Task: `infrastructure/tasks/product_tasks.py`
- Celery Beat Config: `crontab(hour=2, minute=0)`
- Use Case: `BatchUpdateSnapshotsUseCase`
- 並發控制：使用 `asyncio.Semaphore` 限制並發數（避免 Apify rate limit）

**測試案例**：

- 正常流程：更新 10 個產品，全部成功
- 異常流程：其中 2 個產品爬蟲失敗，其他 8 個正常完成
- 效能測試：1000 個產品在 10 分鐘內完成

---

## Epic 4：使用者認證 📝

### Story 4.1：使用者註冊與登入 📝

**狀態**：📝 待辦
**優先級**：🔴 P0（MVP 必須）
**預估工時**：4 小時

**User Story**：

```gherkin
As a 新使用者
I want to 註冊帳號並登入系統
So that 我可以開始追蹤我的產品
```

**驗收標準**：

- [ ] 使用 Supabase Auth 實作認證
- [ ] 支援 Email + Password 註冊/登入
- [ ] （選配）支援 Google OAuth 登入
- [ ] 登入後取得 JWT token
- [ ] 所有 API 請求需帶 Authorization header

**技術實作**：

- 使用 Supabase Auth（不需自己實作）
- API:
  - `POST /auth/signup`（Supabase 提供）
  - `POST /auth/login`（Supabase 提供）
- Middleware: 驗證 JWT token
- Dependency: `get_current_user()`

**測試案例**：

- 註冊新帳號
- 登入成功
- 登入失敗（錯誤密碼）
- 未登入訪問 API → 401

---

## Epic 5：API 文件 📝

### Story 5.1：產生 Swagger/OpenAPI 文件 📝

**狀態**：📝 待辦
**優先級**：🟡 P1（交付要求）
**預估工時**：2 小時

**User Story**：

```gherkin
As a 開發者
I want to 查看 API 文件
So that 我可以了解如何使用 API
```

**驗收標準**：

- [ ] FastAPI 自動生成 Swagger UI：`/docs`
- [ ] 所有 endpoint 有描述
- [ ] Request/Response 有 schema 定義
- [ ] 包含範例資料

**技術實作**：

- FastAPI 內建支援
- 使用 Pydantic models 定義 schema
- 使用 Scalar 生成更美觀的文件（`/scalar`）

---

## 實作優先順序總覽

### Phase 1：MVP 核心功能（P0）

**目標**：展示基本的產品追蹤與警報功能

| Story | 狀態 | 預估工時 |
|-------|------|----------|
| 1.1 新增追蹤產品 | 📝 待辦 | 4h |
| 1.2 查看產品列表 | 📝 待辦 | 3h |
| 2.1 價格變動警報 | 📝 待辦 | 4h |
| 2.2 BSR 變動警報 | 📝 待辦 | 3h |
| 3.1 每日自動更新 | 📝 待辦 | 6h |
| 4.1 使用者認證 | 📝 待辦 | 4h |

**小計**：24 小時（約 3 天）

---

### Phase 2：重要功能（P1）

**目標**：提升使用體驗

| Story | 狀態 | 預估工時 |
|-------|------|----------|
| 1.3 查看歷史趨勢 | 📝 待辦 | 5h |
| 1.4 查看產品詳情 | 📝 待辦 | 2h |
| 1.6 停止追蹤產品 | 📝 待辦 | 2h |
| 2.3 查看警報列表 | 📝 待辦 | 3h |
| 5.1 API 文件 | 📝 待辦 | 2h |

**小計**：14 小時（約 2 天）

---

### Phase 3：Nice to have（P2）

**目標**：錦上添花

| Story | 狀態 | 預估工時 |
|-------|------|----------|
| 1.5 手動更新產品 | 📝 待辦 | 3h |
| 2.4 標記警報已讀 | 📝 待辦 | 1h |

**小計**：4 小時（約 0.5 天）

---

## 完整使用者旅程（End-to-End）

### Day 1：初次使用

```text
時間         | 操作                                    | Story
------------ | --------------------------------------- | ------
08:00        | Sarah 註冊帳號（使用 Email + Password）  | 4.1
08:05        | 登入系統，看到空的產品列表               | 1.2
08:10        | 新增第一個產品：B08ABC1234              | 1.1
08:15        | 系統爬取資料，顯示產品詳情               | 1.1
08:20        | 繼續新增 14 個產品                      | 1.1
08:30        | 查看產品列表，確認所有產品都正常         | 1.2
```

### Day 2：第一次自動更新

```text
時間         | 操作                                    | Story
------------ | --------------------------------------- | ------
02:00        | Celery 自動更新所有 15 個產品           | 3.1
02:05        | 系統檢測到 B08ABC1234 降價 16.7%        | 2.1
02:05        | 生成價格警報記錄                        | 2.1
02:05        | LogNotifier 輸出警報到 console          | 2.1
08:00        | Sarah 登入，看到產品列表有紅色警報標記   | 1.2
08:02        | 查看警報列表，看到價格警報               | 2.3
08:05        | 點擊產品，查看歷史趨勢                   | 1.3
```

### Day 5：手動更新與停止追蹤

```text
時間         | 操作                                    | Story
------------ | --------------------------------------- | ------
10:00        | Sarah 手動點擊「立即更新」某個產品       | 1.5
10:02        | 系統爬取最新資料並更新                   | 1.5
14:00        | Sarah 決定停售某個產品                  | 1.6
14:02        | 點擊「停止追蹤」，產品從列表移除         | 1.6
```

---

## 狀態說明

- 📝 **待辦（Todo）**：尚未開始
- 🚧 **進行中（In Progress）**：正在開發
- ✅ **完成（Done）**：已實作並測試通過
- ⏸️ **暫停（On Hold）**：暫時不做
- ❌ **取消（Cancelled）**：決定不做

---

**最後更新**：2025-10-08
**下一步**：確認優先順序後，開始實作 Phase 1（MVP）
