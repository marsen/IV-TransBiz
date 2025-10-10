# Clean Architecture 重構計劃

**日期**: 2025-10-10
**狀態**: 進行中（已完成 1/3）

---

## 已完成

### ✅ Step 1: 補全 `__init__.py` 檔案

**Commit**: `03aad3f`

**新增檔案**：

- `app/__init__.py`
- `app/domain/__init__.py`
- `app/adapters/api/routers/__init__.py`
- `app/use_cases/health/__init__.py`

**驗證**：

- ✅ 測試通過 (7/7)
- ✅ Ruff format & lint 通過

---

## 待完成

### 🚧 Step 2: config.py 位置討論（需要決策）

**問題**：`app/config.py` 的位置不符合 Clean Architecture

**背景討論**：

1. **config 的性質**：
   - 提供環境變數讀取（`SUPABASE_URL`, `SUPABASE_ANON_KEY`）
   - 包含 fail-fast 驗證邏輯
   - 供所有層使用（adapters、use cases 都可能需要）
   - **結論**：config 是基礎設施（Infrastructure），不是業務邏輯

2. **曾經嘗試的方案（已回退）**：
   - ❌ 移動到 `app/adapters/config.py`
   - **為何回退**：語義不清，config 不是 adapter

---

### 💡 建議方案（3 選 1）

#### **選項 A：建立 Infrastructure 層**（推薦 - 展現架構能力）

```text
app/
├── domain/
├── use_cases/
├── adapters/
└── infrastructure/          # ← 新增
    ├── __init__.py
    └── config.py
```

**優點**：

- ✅ 語義清晰：明確表達「這是基礎設施」
- ✅ 可擴展：未來可加入 logger、metrics、cache 等基礎設施
- ✅ 符合 CA 原則：Infrastructure 是最外層，可被所有層使用
- ✅ 展現架構設計能力（專案評分重點）

**缺點**：

- ❌ 多一層結構（但對大專案有益）

**變更步驟**：

```bash
# 1. 建立 infrastructure 資料夾
mkdir app/infrastructure
touch app/infrastructure/__init__.py

# 2. 移動 config.py
git mv app/config.py app/infrastructure/config.py

# 3. 更新 import (只有 1 個檔案)
# app/adapters/supabase_client.py
- from app.config import SUPABASE_ANON_KEY, SUPABASE_URL
+ from app.infrastructure.config import SUPABASE_ANON_KEY, SUPABASE_URL

# 4. 測試 & Commit
uv run pytest -v
uv run ruff format .
git add .
git commit -m "refactor: move config to infrastructure layer"
```

---

#### **選項 B：保持原位置**（實用主義 - 簡單專案可接受）

```text
app/
├── config.py               # ← 保持不動
├── main.py
├── domain/
├── use_cases/
└── adapters/
```

**優點**：

- ✅ 簡單直接
- ✅ 小專案不需過度分層
- ✅ 不需要任何變更

**缺點**：

- ❌ 根目錄變雜亂（當專案變大時）
- ❌ 沒有明確的分層概念

**決定**：保持現狀，無需動作

---

#### **選項 C：與 main.py 一起視為「Entry Point」**

保持 `app/config.py`，但在文件中註明這是「應用程式啟動層」：

```text
app/
├── config.py               # Application configuration (entry point layer)
├── main.py                 # Application entry point
├── domain/
├── use_cases/
└── adapters/
```

**優點**：

- ✅ 與 main.py 同層，語義統一
- ✅ 簡單實用

**缺點**：

- ❌ 不符合嚴格的 CA 定義

---

### 🎯 決策要點

**如果目標是「展現架構設計能力」** → 選項 A
**如果目標是「快速完成功能」** → 選項 B 或 C

**建議**：考量到專案測試任務中「系統架構設計佔 50%」，**選項 A** 更能展現能力。

---

### ⏸️ Step 3: 建立 system router

**目標**：將 `main.py` 中的業務邏輯移到 router

**變更內容**：

```python
# 建立 app/adapters/api/routers/system.py
@router.get("/")
async def root():
    return {"message": "Amazon Product Monitoring API", "version": "0.1.0"}

@router.get("/favicon.ico")
async def favicon():
    # 移動 favicon 邏輯
    ...
```

**main.py 只保留**：

- FastAPI app 初始化
- Router 註冊
- Scalar docs 設定

---

### ⏸️ Step 4: 重構 main.py

將所有 endpoint 移到對應 router 後，main.py 應該非常簡潔：

```python
"""FastAPI application - Clean Architecture entry point."""

from fastapi import FastAPI
from app.adapters.api.routers import auth, health, system

app = FastAPI(...)

# 註冊 routers
app.include_router(system.router)
app.include_router(health.router)
app.include_router(auth.router)
```

---

## 驗證標準（每個 step）

每次 commit 前必須通過：

```bash
# 1. 測試
uv run pytest -v

# 2. 格式檢查
uv run ruff format .

# 3. Lint 檢查
uv run ruff check .

# 4. Commit
git add <files>
git commit -m "..."
```

---

## 當前狀態總結

- ✅ **Step 1 完成** - `__init__.py` 已補全
- ⏸️ **Step 2 待決策** - config.py 位置需要選擇方案
- ⏸️ **Step 3 待開始** - 建立 system router
- ⏸️ **Step 4 待開始** - 重構 main.py

**預估剩餘時間**：30-40 分鐘

---

## 參考資料

- Clean Architecture 圖解：`docs/plan2.md`
- 當前專案結構：`tree app -I '__pycache__'`
- 測試覆蓋率：7 個測試全通過
