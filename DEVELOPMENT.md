# 開發環境建置指南

本文件說明如何在本地或 Docker 中建置和執行開發環境。

## 前置需求

### 本地開發

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) - Python 套件管理工具

### Docker 開發

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 本地開發環境

### 1. 安裝 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 同步依賴

```bash
# 安裝專案依賴（自動建立虛擬環境）
uv sync

# 安裝開發依賴
uv sync --extra dev
```

### 3. 啟動服務

```bash
# 啟動 API 服務（支援 hot reload）
uv run uvicorn app.main:app --reload

# 指定 port
uv run uvicorn app.main:app --reload --port 8000
```

### 4. 驗證服務

開啟瀏覽器訪問：

- API 文檔：<http://localhost:8000/docs>
- Health Check：<http://localhost:8000/health>

## Docker 開發環境

### 1. 啟動服務

```bash
# 首次啟動或依賴變更後
docker-compose up --build

# 一般啟動
docker-compose up

# 背景執行
docker-compose up -d
```

### 2. 停止服務

```bash
# 停止容器
docker-compose down

# 停止並移除 volumes
docker-compose down -v
```

### 3. 查看日誌

```bash
# 查看即時日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs -f api
```

### 4. 重新建置

當 Dockerfile 或依賴變更時：

```bash
# 清除快取重新建置
docker-compose build --no-cache

# 重新建置並啟動
docker-compose up --build
```

### 5. 驗證服務

開啟瀏覽器訪問：

- API 文檔：<http://localhost:8000/docs>
- Health Check：<http://localhost:8000/health>

## 程式碼品質檢查

### Ruff Linting

```bash
# 檢查程式碼
uv run ruff check .

# 自動修正問題
uv run ruff check --fix .

# 格式化程式碼
uv run ruff format .
```

### 執行測試

```bash
# 執行所有測試
uv run pytest

# 執行特定測試檔案
uv run pytest tests/test_example.py

# 查看測試覆蓋率
uv run pytest --cov=app
```

## 常見問題

### Q1: Docker 啟動失敗，提示 "executable file not found"

**解決方法**：清除 Docker 快取重新建置

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Q2: 本地啟動失敗，找不到模組

**解決方法**：重新同步依賴

```bash
# 刪除現有虛擬環境
rm -rf .venv

# 重新同步
uv sync
```

### Q3: Port 8000 已被佔用

**解決方法**：更改 port 或停止佔用的服務

```bash
# 本地開發使用其他 port
uv run uvicorn app.main:app --reload --port 8001

# 或找出佔用的服務並停止
lsof -ti:8000 | xargs kill -9
```

### Q4: uv 命令找不到

**解決方法**：確認 uv 已安裝並重新載入 shell

```bash
# 重新載入 shell 配置
source ~/.bashrc  # 或 ~/.zshrc

# 驗證 uv 安裝
uv --version
```

## 環境變數設定

目前專案尚未使用環境變數。當需要時：

1. 複製 `.env.example` 為 `.env`
2. 填入必要的配置
3. **切勿將 `.env` 提交至 Git**

## 開發工作流程

1. 啟動開發環境（本地或 Docker）
2. 修改程式碼
3. 執行 linting 和測試
4. 提交變更（遵循 [Conventional Commits](https://www.conventionalcommits.org/)）

```bash
# 提交範例
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in authentication"
git commit -m "docs: update API documentation"
```

## 相關文件

- [專案 README](README.md) - 專案概述與說明
- [TODO 清單](docs/TODO.md) - 當前開發進度
- [技術決策](docs/plan1.md) - 架構與技術選型
