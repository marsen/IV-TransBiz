# Plan 2: Clean Architecture 架構分層設計

## 專案背景

- 延續 Plan 1 的技術棧決策
- 採用 Clean Architecture 原則進行架構分層
- 目標：可測試、可維護、可擴展的系統設計

## Clean Architecture 核心原則

### 依賴規則（The Dependency Rule）

> 依賴方向永遠指向內層，內層不知道外層的存在

```text
外層 → 中層 → 內層
Infrastructure → Adapters → Use Cases → Entities
```

### 關鍵優勢

1. **框架獨立**：業務邏輯不依賴 FastAPI/Supabase 等具體實作
2. **可測試性**：Use Cases 可用 mock 進行單元測試
3. **資料庫獨立**：可抽換 Supabase → PostgreSQL → MongoDB
4. **外部服務獨立**：可抽換 Apify → 自建爬蟲

## 架構分層設計

### 第一層：Domain（領域層/實體層）

**職責**：定義核心業務實體與規則

```text
app/domain/
├── entities/
│   ├── product.py          # Product 實體
│   ├── competitor.py        # Competitor 實體
│   ├── snapshot.py          # ProductSnapshot 實體
│   └── optimization.py      # OptimizationSuggestion 實體
├── value_objects/
│   ├── price.py             # 價格值物件
│   ├── bsr.py               # BSR 值物件
│   └── rating.py            # 評分值物件
└── repositories/            # Repository 介面（抽象）
    ├── product_repository.py
    ├── competitor_repository.py
    └── snapshot_repository.py
```

**特性**：

- 純 Python dataclass 或 Pydantic BaseModel
- 無外部依賴（不 import FastAPI/SQLAlchemy/Supabase）
- 包含業務驗證邏輯（如：價格不能為負）

### 第二層：Use Cases（應用層）

**職責**：編排業務邏輯流程

```text
app/use_cases/
├── product/
│   ├── track_product.py         # 新增追蹤產品
│   ├── update_product_data.py   # 更新產品資料
│   └── get_product_history.py   # 查詢歷史資料
├── competitor/
│   ├── analyze_competitors.py   # 競品分析
│   └── compare_metrics.py       # 指標比較
├── optimization/
│   ├── generate_suggestions.py  # 生成優化建議
│   └── evaluate_listing.py      # Listing 評估
└── ports/                       # 外部服務介面（Port）
    ├── scraper_port.py          # 爬蟲服務介面
    ├── ai_service_port.py       # AI 服務介面
    └── notification_port.py     # 通知服務介面
```

**特性**：

- 依賴注入 Repository 介面（抽象）
- 定義 Port（介面）給外部服務
- 包含業務邏輯編排（如：先爬資料 → 儲存 → 通知）

### 第三層：Adapters（介面適配層）

**職責**：轉換資料格式，實作外層與內層的介面

```text
app/adapters/
├── api/                         # Web API 層
│   ├── v1/
│   │   ├── products.py          # Product endpoints
│   │   ├── competitors.py       # Competitor endpoints
│   │   └── optimizations.py     # Optimization endpoints
│   ├── schemas/                 # Pydantic request/response schemas
│   └── dependencies.py          # FastAPI dependencies
├── repositories/                # Repository 實作
│   ├── supabase_product_repo.py
│   ├── supabase_competitor_repo.py
│   └── redis_cache_repo.py
└── external/                    # 外部服務適配器（Adapter）
    ├── apify_scraper.py         # 實作 ScraperPort
    ├── openai_service.py        # 實作 AIServicePort
    └── email_notifier.py        # 實作 NotificationPort
```

**特性**：

- `api/` 負責 HTTP 請求/回應轉換
- `repositories/` 實作 domain 定義的介面
- `external/` 實作 use_cases/ports 定義的介面

### 第四層：Infrastructure（基礎設施層）

**職責**：具體技術實作與設定

```text
app/infrastructure/
├── database/
│   ├── supabase.py              # Supabase 連線設定
│   └── models.py                # SQLAlchemy models（如果需要 ORM）
├── cache/
│   ├── redis.py                 # Redis 連線設定
│   └── cache_strategy.py        # 快取策略實作
├── tasks/
│   ├── celery_app.py            # Celery 設定
│   ├── scraping_tasks.py        # 爬蟲任務
│   └── analysis_tasks.py        # 分析任務
├── config/
│   ├── settings.py              # 環境變數設定
│   └── logging.py               # Log 設定
└── main.py                      # FastAPI app 初始化
```

**特性**：

- 框架相關設定（FastAPI, Celery, Redis）
- 第三方服務連線初始化
- 環境變數與設定管理

## 待討論問題

### Q1: Celery 任務的定位

**選項 A（Infrastructure）**：

```python
# infrastructure/tasks/scraping_tasks.py
@celery_app.task
def scrape_product_task(product_id: str):
    # 直接呼叫 use case
    use_case = UpdateProductDataUseCase(...)
    use_case.execute(product_id)
```

**選項 B（Use Case 定義介面）**：

```python
# use_cases/ports/task_scheduler_port.py
class TaskSchedulerPort(ABC):
    @abstractmethod
    def schedule_scraping(self, product_id: str): pass

# infrastructure/tasks/celery_scheduler.py
class CeleryScheduler(TaskSchedulerPort):
    def schedule_scraping(self, product_id: str):
        scrape_product_task.delay(product_id)
```

**你的偏好？**

### Q2: 外部服務呼叫方式 ✅ 已決策：Port/Adapter 模式

**決策**：使用 Port/Adapter 模式，並將職責分離

#### 架構層次

```text
Use Case Layer
    ↓ 依賴（抽象介面）
Adapter Layer（轉換邏輯）
    ↓ 呼叫
Infrastructure Layer（技術實作）
```

#### 完整範例：Apify 爬蟲

**1. Port 定義（Use Case 層）**

```python
# use_cases/ports/scraper_port.py
from abc import ABC, abstractmethod
from domain.entities.product import Product

class ScraperPort(ABC):
    """爬蟲服務介面 - Use Case 只依賴這個抽象介面"""

    @abstractmethod
    async def scrape_product(self, asin: str) -> Product:
        """爬取產品資料並回傳 Domain Entity"""
        pass
```

**2. Adapter 實作（Adapter 層）**

```python
# adapters/external/apify_scraper.py
from use_cases.ports.scraper_port import ScraperPort
from infrastructure.external.apify_client import ApifyClient
from domain.entities.product import Product

class ApifyScraper(ScraperPort):
    """Apify API 的 Adapter - 負責資料轉換"""

    def __init__(self, client: ApifyClient):
        self.client = client  # 注入 Infrastructure 的 HTTP client

    async def scrape_product(self, asin: str) -> Product:
        # 1. 呼叫底層 client
        raw_data = await self.client.fetch_product_details(asin)

        # 2. 轉換為 Domain Entity
        return Product(
            asin=raw_data["asin"],
            title=raw_data["title"],
            price=raw_data["price"]["value"],
            currency=raw_data["price"]["currency"],
            # ... 其他欄位轉換
        )
```

**3. Infrastructure Client（Infrastructure 層）**

```python
# infrastructure/external/apify_client.py
import httpx
from infrastructure.config.settings import settings

class ApifyClient:
    """Apify HTTP Client - 負責低階 API 呼叫"""

    def __init__(self):
        self.api_key = settings.APIFY_API_KEY
        self.base_url = "https://api.apify.com/v2"

    async def fetch_product_details(self, asin: str) -> dict:
        """呼叫 Apify Actor 並回傳原始 JSON"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/acts/junglee~amazon-crawler/runs",
                json={"asin": asin},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return response.json()
```

**4. Use Case 使用（Use Case 層）**

```python
# use_cases/product/update_product_data.py
from use_cases.ports.scraper_port import ScraperPort
from domain.repositories.product_repository import ProductRepository

class UpdateProductDataUseCase:
    def __init__(
        self,
        scraper: ScraperPort,  # 只依賴抽象介面
        repository: ProductRepository
    ):
        self.scraper = scraper
        self.repository = repository

    async def execute(self, asin: str):
        # 透過 Port 呼叫，不知道是 Apify 還是其他實作
        product = await self.scraper.scrape_product(asin)
        await self.repository.save(product)
```

#### 職責分離總結

| 層級 | 檔案 | 職責 |
|------|------|------|
| Use Case | `ports/scraper_port.py` | 定義介面（抽象） |
| Adapter | `adapters/external/apify_scraper.py` | 資料轉換（Apify JSON → Domain Entity） |
| Infrastructure | `infrastructure/external/apify_client.py` | HTTP 呼叫、連線管理、認證 |

#### 優勢

1. **可測試性**：Use Case 測試時可 mock ScraperPort
2. **可替換性**：未來可實作 `SelfHostedScraper` 替換 Apify
3. **符合依賴規則**：Use Case 不依賴具體的 HTTP client
4. **關注點分離**：
   - Adapter 專注於格式轉換
   - Infrastructure 專注於技術細節（HTTP、認證、重試）

### Q3: Dependency Injection 方案 ✅ 已決策：FastAPI Depends

**決策**：使用 FastAPI Depends，採用混合策略（Singleton for stateful, Factory for stateless）

#### 設計原則

| 依賴類型 | Pattern | 理由 | 範例 |
|---------|---------|------|------|
| **有狀態**（連線池、client） | Singleton | 避免重複建立連線 | Supabase client, Redis client |
| **無狀態**（Repository、Service） | Factory | 每次請求建立新實例 | ProductRepository, Use Case |
| **設定檔** | Singleton | 應用程式啟動時載入一次 | Settings |

#### 實作架構

```text
adapters/api/
├── dependencies.py          # 所有 dependency 定義
└── lifespan.py              # FastAPI lifespan (管理 Singleton)
```

#### 完整實作範例

**1. Lifespan 管理（Singleton 生命週期）**

```python
# adapters/api/lifespan.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from infrastructure.database.supabase import SupabaseClient
from infrastructure.cache.redis import RedisClient
from infrastructure.external.apify_client import ApifyClient

# 全域 Singleton 實例
class AppState:
    """應用程式全域狀態 - 在 lifespan 中初始化"""
    supabase_client: SupabaseClient | None = None
    redis_client: RedisClient | None = None
    apify_client: ApifyClient | None = None

app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan - 啟動時建立連線，關閉時清理"""
    # Startup
    print("🚀 Initializing application...")

    # 初始化 Singleton 依賴（有狀態）
    app_state.supabase_client = SupabaseClient()
    app_state.redis_client = await RedisClient.create()
    app_state.apify_client = ApifyClient()

    print("✅ All connections established")

    yield  # 應用程式運行中

    # Shutdown
    print("🛑 Shutting down...")
    await app_state.redis_client.close()
    print("✅ Cleanup complete")
```

**2. Dependencies 定義**

```python
# adapters/api/dependencies.py
from typing import Annotated
from fastapi import Depends
from adapters.api.lifespan import app_state

# ============= Infrastructure 層（Singleton） =============

def get_supabase_client():
    """取得 Supabase Client（Singleton）"""
    if app_state.supabase_client is None:
        raise RuntimeError("Supabase client not initialized")
    return app_state.supabase_client

def get_redis_client():
    """取得 Redis Client（Singleton）"""
    if app_state.redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return app_state.redis_client

def get_apify_client():
    """取得 Apify Client（Singleton）"""
    if app_state.apify_client is None:
        raise RuntimeError("Apify client not initialized")
    return app_state.apify_client

# ============= Adapter 層（Factory - 每次建立新實例） =============

def get_product_repository(
    supabase: Annotated[SupabaseClient, Depends(get_supabase_client)],
    redis: Annotated[RedisClient, Depends(get_redis_client)]
):
    """建立 ProductRepository（Factory）"""
    from adapters.repositories.supabase_product_repo import SupabaseProductRepository
    return SupabaseProductRepository(supabase_client=supabase, cache=redis)

def get_apify_scraper(
    client: Annotated[ApifyClient, Depends(get_apify_client)]
):
    """建立 ApifyScraper（Factory）"""
    from adapters.external.apify_scraper import ApifyScraper
    return ApifyScraper(client=client)

def get_openai_service(
    redis: Annotated[RedisClient, Depends(get_redis_client)]
):
    """建立 OpenAIService（Factory）"""
    from adapters.external.openai_service import OpenAIService
    return OpenAIService(cache=redis)

# ============= Use Case 層（Factory） =============

def get_track_product_use_case(
    repository: Annotated[ProductRepository, Depends(get_product_repository)],
    scraper: Annotated[ScraperPort, Depends(get_apify_scraper)]
):
    """建立 TrackProductUseCase（Factory）"""
    from use_cases.product.track_product import TrackProductUseCase
    return TrackProductUseCase(
        repository=repository,
        scraper=scraper
    )

def get_generate_suggestions_use_case(
    product_repo: Annotated[ProductRepository, Depends(get_product_repository)],
    ai_service: Annotated[AIServicePort, Depends(get_openai_service)]
):
    """建立 GenerateSuggestionsUseCase（Factory）"""
    from use_cases.optimization.generate_suggestions import GenerateSuggestionsUseCase
    return GenerateSuggestionsUseCase(
        product_repository=product_repo,
        ai_service=ai_service
    )

# ============= 型別別名（簡化使用） =============

# 定義常用的 Annotated 型別
SupabaseDep = Annotated[SupabaseClient, Depends(get_supabase_client)]
RedisDep = Annotated[RedisClient, Depends(get_redis_client)]
ProductRepoDep = Annotated[ProductRepository, Depends(get_product_repository)]
TrackProductUseCaseDep = Annotated[TrackProductUseCase, Depends(get_track_product_use_case)]
```

**3. API Endpoint 使用**

```python
# adapters/api/v1/products.py
from fastapi import APIRouter, Depends
from adapters.api.dependencies import TrackProductUseCaseDep
from adapters.api.schemas.product import CreateProductRequest, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    request: CreateProductRequest,
    use_case: TrackProductUseCaseDep  # 使用型別別名，簡潔！
):
    """追蹤新產品"""
    product = await use_case.execute(asin=request.asin)
    return ProductResponse.from_entity(product)

@router.get("/{product_id}/suggestions")
async def get_suggestions(
    product_id: str,
    use_case: Annotated[GenerateSuggestionsUseCase, Depends(get_generate_suggestions_use_case)]
):
    """取得產品優化建議"""
    suggestions = await use_case.execute(product_id=product_id)
    return {"suggestions": suggestions}
```

**4. FastAPI App 初始化**

```python
# app/main.py
from fastapi import FastAPI
from adapters.api.lifespan import lifespan
from adapters.api.v1 import products, competitors

app = FastAPI(
    title="Amazon Product Monitor",
    version="0.1.0",
    lifespan=lifespan  # 註冊 lifespan
)

# 註冊 routers
app.include_router(products.router, prefix="/api/v1")
app.include_router(competitors.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### 有狀態依賴的處理策略

**問題**：DB connection pool 如何管理？

**方案**：在 lifespan 中初始化，透過 Depends 取得

```python
# infrastructure/database/supabase.py
from supabase import create_client, Client
from infrastructure.config.settings import settings

class SupabaseClient:
    """Supabase Client Wrapper - 管理連線池"""

    def __init__(self):
        self.client: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
        # Supabase Python client 內建連線池管理

    async def execute_query(self, table: str, operation: str, **kwargs):
        """執行資料庫操作"""
        return getattr(self.client.table(table), operation)(**kwargs)

    def __del__(self):
        """清理連線（如果需要）"""
        # Supabase client 會自動管理
        pass
```

```python
# infrastructure/cache/redis.py
import redis.asyncio as redis
from infrastructure.config.settings import settings

class RedisClient:
    """Redis Client Wrapper - 管理連線池"""

    def __init__(self, pool: redis.ConnectionPool):
        self.pool = pool
        self.client = redis.Redis(connection_pool=pool)

    @classmethod
    async def create(cls):
        """Factory method - 建立連線池"""
        pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=10,
            decode_responses=True
        )
        return cls(pool)

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int):
        await self.client.setex(key, ttl, value)

    async def close(self):
        """關閉連線池"""
        await self.client.close()
        await self.pool.disconnect()
```

#### 依賴注入流程圖

```text
HTTP Request
    ↓
FastAPI Endpoint
    ↓
Depends(get_track_product_use_case)  ← Factory（每次建立新實例）
    ↓ 需要
Depends(get_product_repository)      ← Factory（每次建立新實例）
    ↓ 需要
Depends(get_supabase_client)         ← Singleton（app_state）
    ↓
返回同一個 SupabaseClient 實例（連線池）
```

#### 測試支援

**問題**：測試時如何 override dependencies？

```python
# tests/api/test_products.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from app.main import app
from adapters.api.dependencies import get_track_product_use_case

def test_create_product():
    # 建立 mock use case
    mock_use_case = Mock()
    mock_use_case.execute.return_value = Product(asin="B08N5WRWNW", ...)

    # Override dependency
    app.dependency_overrides[get_track_product_use_case] = lambda: mock_use_case

    # 測試
    with TestClient(app) as client:
        response = client.post("/api/v1/products", json={"asin": "B08N5WRWNW"})
        assert response.status_code == 201

    # 清理
    app.dependency_overrides.clear()
```

#### 優勢總結

1. **簡單直觀**：不需要額外的 DI 框架
2. **型別安全**：`Annotated` 提供完整的型別提示
3. **效能優化**：Singleton 避免重複建立連線
4. **測試友善**：`dependency_overrides` 機制簡單
5. **生命週期管理**：`lifespan` 確保資源正確初始化與清理

#### 注意事項

1. **Thread Safety**：`app_state` 是全域變數，但 FastAPI 是 async，不需擔心 race condition
2. **連線池**：Supabase/Redis client 內建連線池，Singleton 即可
3. **記憶體洩漏**：確保 `lifespan` 的 shutdown 階段關閉所有連線

## 資料流範例

### Use Case: 追蹤新產品

```text
1. API Layer（Adapter）
   POST /api/v1/products {"asin": "B08N5WRWNW"}
   ↓
2. Use Case Layer
   TrackProductUseCase.execute(asin)
   ├── 透過 ScraperPort 呼叫爬蟲
   ├── 建立 Product Entity
   ├── 透過 ProductRepository 儲存
   └── 透過 NotificationPort 發送通知
   ↓
3. Adapter Layer
   ├── ApifyScraper.scrape_product()      # 實作 ScraperPort
   ├── SupabaseProductRepo.save()         # 實作 ProductRepository
   └── EmailNotifier.send()                # 實作 NotificationPort
   ↓
4. Infrastructure Layer
   ├── Supabase 連線執行 SQL
   ├── Redis 快取產品資料
   └── SMTP 發送 Email
```

### Use Case: 生成優化建議

```text
1. API Layer
   GET /api/v1/products/{id}/suggestions
   ↓
2. Use Case Layer
   GenerateSuggestionsUseCase.execute(product_id)
   ├── 透過 ProductRepository 取得產品
   ├── 透過 CompetitorRepository 取得競品
   ├── 透過 AIServicePort 呼叫 OpenAI
   └── 儲存 OptimizationSuggestion Entity
   ↓
3. Adapter Layer
   ├── SupabaseProductRepo.find_by_id()
   ├── SupabaseCompetitorRepo.find_by_product()
   ├── OpenAIService.generate_suggestions()   # 實作 AIServicePort
   └── SupabaseOptimizationRepo.save()
   ↓
4. Infrastructure Layer
   ├── Supabase 查詢
   ├── OpenAI API 呼叫
   ├── Redis 快取建議（24h TTL）
   └── Supabase 儲存
```

## 測試策略

### 單元測試（Use Case Layer）

```python
# tests/use_cases/test_track_product.py
def test_track_product_use_case():
    # Arrange
    mock_scraper = Mock(spec=ScraperPort)
    mock_repo = Mock(spec=ProductRepository)
    use_case = TrackProductUseCase(
        scraper=mock_scraper,
        repository=mock_repo
    )

    # Act
    use_case.execute(asin="B08N5WRWNW")

    # Assert
    mock_scraper.scrape_product.assert_called_once()
    mock_repo.save.assert_called_once()
```

### 整合測試（Adapter Layer）

```python
# tests/adapters/test_apify_scraper.py
@pytest.mark.asyncio
async def test_apify_scraper_integration():
    scraper = ApifyScraper(api_key=TEST_API_KEY)
    result = await scraper.scrape_product("B08N5WRWNW")
    assert result.asin == "B08N5WRWNW"
    assert result.price > 0
```

### E2E 測試（API Layer）

```python
# tests/api/test_products_endpoint.py
def test_create_product_endpoint(client: TestClient):
    response = client.post("/api/v1/products", json={"asin": "B08N5WRWNW"})
    assert response.status_code == 201
    assert response.json()["asin"] == "B08N5WRWNW"
```

## 錯誤處理策略（最終防線模式）

### 錯誤處理設計原則

**最終防線（Last Line of Defense）**：在 API 層使用全域 Exception Handler 捕捉所有錯誤，確保：

1. 不會有未處理的例外暴露給客戶端
2. 所有錯誤都以統一格式回應
3. 敏感資訊不會洩漏

### 錯誤分層架構

```text
1. Domain Layer (領域錯誤)
   ├── ProductNotFoundError
   ├── InvalidPriceError
   └── BusinessRuleViolationError

2. Use Case Layer (應用錯誤)
   ├── ScrapingFailedError
   ├── AIServiceUnavailableError
   └── ResourceConflictError

3. Infrastructure Layer (技術錯誤)
   ├── DatabaseConnectionError
   ├── ExternalAPIError
   └── CacheError

4. API Layer (HTTP 錯誤) ← 最終防線
   └── Global Exception Handler
       ├── 捕捉所有上層錯誤
       ├── 轉換為 HTTP 狀態碼
       └── 回傳標準錯誤格式
```

### 實作設計

#### 1. Domain Layer - 自訂 Exception

```python
# domain/exceptions.py
class DomainException(Exception):
    """Domain 層基礎 Exception"""
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ProductNotFoundError(DomainException):
    def __init__(self, product_id: str):
        super().__init__(
            message=f"Product {product_id} not found",
            error_code="PRODUCT_NOT_FOUND"
        )

class InvalidPriceError(DomainException):
    def __init__(self, price: float):
        super().__init__(
            message=f"Invalid price: {price}. Price must be positive",
            error_code="INVALID_PRICE"
        )

class BusinessRuleViolationError(DomainException):
    """業務規則違反（如：超過追蹤產品數量上限）"""
    pass
```

#### 2. Use Case Layer - 應用錯誤

```python
# use_cases/exceptions.py
class UseCaseException(Exception):
    """Use Case 層基礎 Exception"""
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ScrapingFailedError(UseCaseException):
    def __init__(self, asin: str, reason: str):
        super().__init__(
            message=f"Failed to scrape product {asin}: {reason}",
            error_code="SCRAPING_FAILED"
        )

class AIServiceUnavailableError(UseCaseException):
    def __init__(self):
        super().__init__(
            message="AI service is temporarily unavailable",
            error_code="AI_SERVICE_UNAVAILABLE"
        )
```

#### 3. Infrastructure Layer - 技術錯誤

```python
# infrastructure/exceptions.py
class InfrastructureException(Exception):
    """Infrastructure 層基礎 Exception"""
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class DatabaseConnectionError(InfrastructureException):
    def __init__(self, details: str):
        super().__init__(
            message=f"Database connection failed: {details}",
            error_code="DB_CONNECTION_ERROR"
        )

class ExternalAPIError(InfrastructureException):
    def __init__(self, service: str, status_code: int):
        super().__init__(
            message=f"External API {service} failed with status {status_code}",
            error_code="EXTERNAL_API_ERROR"
        )
```

#### 4. API Layer - 全域 Exception Handler（最終防線）

```python
# adapters/api/exception_handlers.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from domain.exceptions import DomainException
from use_cases.exceptions import UseCaseException
from infrastructure.exceptions import InfrastructureException
import logging

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI):
    """註冊所有 Exception Handlers"""

    # Domain 錯誤 → 400 Bad Request
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        logger.warning(f"Domain error: {exc.message}", extra={"error_code": exc.error_code})
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "type": "domain_error"
                }
            }
        )

    # Use Case 錯誤 → 422 Unprocessable Entity 或 503
    @app.exception_handler(UseCaseException)
    async def use_case_exception_handler(request: Request, exc: UseCaseException):
        # 根據錯誤類型決定 HTTP 狀態碼
        if "UNAVAILABLE" in exc.error_code:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        logger.error(f"Use case error: {exc.message}", extra={"error_code": exc.error_code})
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "type": "use_case_error"
                }
            }
        )

    # Infrastructure 錯誤 → 500 Internal Server Error
    @app.exception_handler(InfrastructureException)
    async def infrastructure_exception_handler(request: Request, exc: InfrastructureException):
        logger.error(f"Infrastructure error: {exc.message}", extra={"error_code": exc.error_code})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": "An internal error occurred",  # 不洩漏細節
                    "type": "infrastructure_error"
                }
            }
        )

    # 未預期錯誤 → 500（最終防線）
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.critical(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "type": "system_error"
                }
            }
        )
```

#### 5. 標準 Response 格式

```python
# adapters/api/schemas/response.py
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class ErrorDetail(BaseModel):
    """錯誤詳情"""
    code: str
    message: str
    type: str  # domain_error, use_case_error, infrastructure_error, system_error

class APIResponse(BaseModel, Generic[T]):
    """統一 API Response 格式"""
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None

# 使用範例
class ProductResponse(BaseModel):
    asin: str
    title: str
    price: float

# Success Response
{
    "success": true,
    "data": {
        "asin": "B08N5WRWNW",
        "title": "Example Product",
        "price": 29.99
    },
    "error": null
}

# Error Response
{
    "success": false,
    "data": null,
    "error": {
        "code": "PRODUCT_NOT_FOUND",
        "message": "Product B08N5WRWNW not found",
        "type": "domain_error"
    }
}
```

#### 6. FastAPI App 初始化

```python
# app/main.py
from fastapi import FastAPI
from adapters.api.exception_handlers import register_exception_handlers
from adapters.api.lifespan import lifespan

app = FastAPI(
    title="Amazon Product Monitor",
    version="0.1.0",
    lifespan=lifespan
)

# 註冊全域 Exception Handlers（最終防線）
register_exception_handlers(app)

# 註冊 routers
app.include_router(products.router, prefix="/api/v1")
```

### 錯誤碼對照表

| 錯誤碼 | HTTP Status | 說明 | 層級 |
|--------|-------------|------|------|
| `PRODUCT_NOT_FOUND` | 404 | 產品不存在 | Domain |
| `INVALID_PRICE` | 400 | 價格格式錯誤 | Domain |
| `SCRAPING_FAILED` | 422 | 爬蟲失敗 | Use Case |
| `AI_SERVICE_UNAVAILABLE` | 503 | AI 服務不可用 | Use Case |
| `DB_CONNECTION_ERROR` | 500 | 資料庫連線失敗 | Infrastructure |
| `EXTERNAL_API_ERROR` | 500 | 外部 API 錯誤 | Infrastructure |
| `INTERNAL_SERVER_ERROR` | 500 | 未預期錯誤 | System |

### 使用範例

```python
# use_cases/product/track_product.py
from domain.exceptions import ProductNotFoundError
from use_cases.exceptions import ScrapingFailedError

class TrackProductUseCase:
    async def execute(self, asin: str):
        # 爬取產品資料
        try:
            product_data = await self.scraper.scrape_product(asin)
        except Exception as e:
            # 轉換為 Use Case 層錯誤
            raise ScrapingFailedError(asin=asin, reason=str(e))

        # 檢查產品是否存在
        existing = await self.repository.find_by_asin(asin)
        if existing:
            raise ProductNotFoundError(product_id=asin)  # 會被 API 層轉為 404

        # 儲存產品
        await self.repository.save(product_data)
```

### 錯誤處理優勢

1. **分層清晰**：每層定義自己的錯誤類型
2. **最終防線**：全域 Handler 確保不會有裸露的 500 錯誤
3. **統一格式**：所有錯誤回應格式一致
4. **安全性**：Infrastructure 錯誤不洩漏敏感資訊
5. **可追蹤**：錯誤碼 + 日誌方便 debug

## 下一步行動

1. **討論並確認上述 Q1~Q3 的技術決策**
2. 建立基礎目錄結構
3. 定義核心 Entity（Product, Competitor, Snapshot）
4. 實作錯誤處理架構（最終防線模式）
5. 實作第一個 Use Case（TrackProductUseCase）
6. 撰寫對應的單元測試

---

**記錄日期**：2025-10-08
**參考文件**：plan1.md, Clean Architecture (Robert C. Martin)
