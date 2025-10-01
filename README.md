# Amazon Product Monitoring & Optimization Tool

## 開發原則

1. **過早優化是萬惡之源，切勿畫蛇添足** — Donald Knuth
2. **需要時才建立**，避免過度設計
3. **先列 TODO，後動手**：所有工作需先寫入 `docs/TODO.md` 並排序；初期可接受抽象項目，但執行前必須具體化

## 快速開始

### 方法一：使用 Docker

```bash
docker-compose up
```

### 方法二：本地執行

```bash
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
