# Amazon Product Monitoring & Optimization Tool

## 開發原則

1. **過早優化是萬惡之源，切勿畫蛇添足** — Donald Knuth
2. **需要時才建立**，避免過度設計
3. **先列 TODO，後動手**：所有工作需先寫入 `docs/TODO.md` 並排序；初期可接受抽象項目，但執行前必須具體化
4. **Commit 遵循 Conventional Commits**：格式為 `<type>: <description>`

### Commit 規範

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```text
<type>: <subject>

<body>

<footer>
```

**Type 類型**：

- `feat`: 新功能
- `fix`: 修復 bug
- `docs`: 文件變更
- `style`: 格式調整（不影響程式碼運行）
- `refactor`: 重構（不是新功能也不是修 bug）
- `test`: 測試相關
- `chore`: 建構工具或輔助工具變更

**範例**：

```bash
feat: add product tracking endpoint
fix: resolve database connection timeout
docs: update API documentation
refactor: simplify health check logic
```

## 快速開始

### 方法一：使用 Docker

```bash
docker-compose up
```

### 方法二：本地執行

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt

# 啟動服務
uvicorn app.main:app --reload
```

訪問 <http://localhost:8000/docs> 查看 API 文件

## API 端點

- `GET /` - 首頁
- `GET /health` - 健康檢查

## 下一步

參考 `docs/plan1.md` 了解技術規劃與待辦事項。

## License

Proprietary - Transbiz Co.
