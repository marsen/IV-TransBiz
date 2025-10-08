# Plan 3: 產品資料追蹤系統 - Clean Architecture 實作設計

## 需求分析

### 功能需求

**選項 1：產品資料追蹤系統**

- **系統規模**：設計支援 1000+ 產品，Demo 使用 10-20 個同類別產品
- **追蹤項目**：
  - 價格變化
  - BSR (Best Sellers Rank) 趨勢
  - 評分與評論數變化
  - Buy Box 價格
- **更新頻率**：每日一次
- **異常通知**：
  - 價格變動 > 10%
  - 小類別 BSR 變動 > 30%
- **技術要求**：
  - 使用 Apify Actor 擷取產品資料
  - Redis 快取機制（24-48 小時）
  - 背景任務排程（每日更新）
  - 資料變化追蹤與通知系統

### 非功能需求

- **效能**：支援 1000+ 產品的每日更新
- **可靠性**：爬蟲失敗時的重試機制
- **可擴展性**：未來可增加追蹤項目
- **成本控制**：使用快取減少 Apify API 呼叫

## Clean Architecture 分層設計

### 1. Domain Layer（領域層）

#### Entities（實體）

```python
# domain/entities/product.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal

@dataclass
class Product:
    """產品主實體"""
    id: str  # UUID
    asin: str  # Amazon 產品 ID
    title: str
    category: str
    user_id: str  # 追蹤此產品的使用者
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        """驗證業務規則"""
        if not self.asin or len(self.asin) != 10:
            raise ValueError("ASIN must be 10 characters")

@dataclass
class ProductSnapshot:
    """產品快照 - 時序資料"""
    id: str
    product_id: str  # FK to Product
    asin: str

    # 追蹤項目
    price: Optional[Decimal]
    currency: str
    bsr_main: Optional[int]  # 主類別 BSR
    bsr_sub: Optional[int]   # 小類別 BSR
    rating: Optional[float]
    review_count: Optional[int]
    buybox_price: Optional[Decimal]

    # 元資料
    scraped_at: datetime
    created_at: datetime

    def calculate_price_change_percentage(self, previous_snapshot: 'ProductSnapshot') -> float:
        """計算價格變化百分比"""
        if not self.price or not previous_snapshot.price:
            return 0.0
        return float((self.price - previous_snapshot.price) / previous_snapshot.price * 100)

    def calculate_bsr_change_percentage(self, previous_snapshot: 'ProductSnapshot') -> float:
        """計算 BSR 變化百分比（小類別）"""
        if not self.bsr_sub or not previous_snapshot.bsr_sub:
            return 0.0
        return float((self.bsr_sub - previous_snapshot.bsr_sub) / previous_snapshot.bsr_sub * 100)

@dataclass
class ChangeAlert:
    """變化警報實體"""
    id: str
    product_id: str
    alert_type: str  # PRICE_CHANGE, BSR_CHANGE
    change_percentage: float
    old_value: float
    new_value: float
    triggered_at: datetime
    notified: bool = False

    def should_trigger(self, threshold: float) -> bool:
        """判斷是否應觸發警報"""
        return abs(self.change_percentage) >= threshold
```

#### Value Objects（值物件）

```python
# domain/value_objects/price.py
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Price:
    """價格值物件"""
    value: Decimal
    currency: str

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Price cannot be negative")
        if self.currency not in ["USD", "EUR", "JPY", "TWD"]:
            raise ValueError(f"Unsupported currency: {self.currency}")

@dataclass(frozen=True)
class BSR:
    """Best Sellers Rank 值物件"""
    rank: int
    category: str

    def __post_init__(self):
        if self.rank < 1:
            raise ValueError("BSR rank must be positive")
```

#### Repository Interfaces（倉儲介面）

```python
# domain/repositories/product_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.product import Product, ProductSnapshot

class ProductRepository(ABC):
    """產品倉儲介面"""

    @abstractmethod
    async def save(self, product: Product) -> Product:
        """儲存產品"""
        pass

    @abstractmethod
    async def find_by_id(self, product_id: str) -> Optional[Product]:
        """依 ID 查詢產品"""
        pass

    @abstractmethod
    async def find_by_asin(self, asin: str) -> Optional[Product]:
        """依 ASIN 查詢產品"""
        pass

    @abstractmethod
    async def find_all_active(self) -> List[Product]:
        """查詢所有啟用的產品"""
        pass

    @abstractmethod
    async def delete(self, product_id: str) -> bool:
        """刪除產品"""
        pass

class SnapshotRepository(ABC):
    """快照倉儲介面"""

    @abstractmethod
    async def save(self, snapshot: ProductSnapshot) -> ProductSnapshot:
        """儲存快照"""
        pass

    @abstractmethod
    async def find_latest_by_product(self, product_id: str) -> Optional[ProductSnapshot]:
        """取得產品最新快照"""
        pass

    @abstractmethod
    async def find_by_product_id(self, product_id: str, limit: int = 30) -> List[ProductSnapshot]:
        """取得產品歷史快照"""
        pass

    @abstractmethod
    async def find_previous_snapshot(self, product_id: str, before: datetime) -> Optional[ProductSnapshot]:
        """取得指定時間之前的快照"""
        pass
```

### 2. Use Case Layer（應用層）

#### Use Cases

```python
# use_cases/product/track_product.py
from domain.entities.product import Product
from domain.repositories.product_repository import ProductRepository
from use_cases.ports.scraper_port import ScraperPort
from use_cases.exceptions import ProductAlreadyExistsError

class TrackProductUseCase:
    """追蹤新產品 Use Case"""

    def __init__(
        self,
        product_repository: ProductRepository,
        scraper: ScraperPort
    ):
        self.repository = product_repository
        self.scraper = scraper

    async def execute(self, asin: str, user_id: str) -> Product:
        """
        執行追蹤產品

        1. 檢查產品是否已存在
        2. 透過 Apify 爬取產品基本資訊
        3. 建立 Product 實體
        4. 儲存到資料庫
        """
        # 檢查是否已存在
        existing = await self.repository.find_by_asin(asin)
        if existing:
            raise ProductAlreadyExistsError(asin=asin)

        # 爬取產品資訊
        product_data = await self.scraper.scrape_product(asin)

        # 建立實體
        product = Product(
            id=generate_uuid(),
            asin=asin,
            title=product_data.title,
            category=product_data.category,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # 儲存
        return await self.repository.save(product)


# use_cases/product/update_product_snapshot.py
from domain.entities.product import ProductSnapshot, ChangeAlert
from domain.repositories.product_repository import ProductRepository, SnapshotRepository
from use_cases.ports.scraper_port import ScraperPort
from use_cases.ports.notification_port import NotificationPort

class UpdateProductSnapshotUseCase:
    """更新產品快照 Use Case"""

    def __init__(
        self,
        product_repository: ProductRepository,
        snapshot_repository: SnapshotRepository,
        scraper: ScraperPort,
        notifier: NotificationPort
    ):
        self.product_repo = product_repository
        self.snapshot_repo = snapshot_repository
        self.scraper = scraper
        self.notifier = notifier

    async def execute(self, product_id: str) -> ProductSnapshot:
        """
        執行更新產品快照

        1. 取得產品資訊
        2. 爬取最新資料
        3. 建立新快照
        4. 比較與前次快照的差異
        5. 觸發異常警報（如果需要）
        6. 儲存快照
        """
        # 1. 取得產品
        product = await self.product_repo.find_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id=product_id)

        # 2. 爬取最新資料
        data = await self.scraper.scrape_product(product.asin)

        # 3. 建立新快照
        snapshot = ProductSnapshot(
            id=generate_uuid(),
            product_id=product_id,
            asin=product.asin,
            price=data.price,
            currency=data.currency,
            bsr_main=data.bsr_main,
            bsr_sub=data.bsr_sub,
            rating=data.rating,
            review_count=data.review_count,
            buybox_price=data.buybox_price,
            scraped_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )

        # 4. 取得前次快照並比較
        previous = await self.snapshot_repo.find_latest_by_product(product_id)
        if previous:
            await self._check_and_notify_changes(snapshot, previous)

        # 5. 儲存快照
        return await self.snapshot_repo.save(snapshot)

    async def _check_and_notify_changes(
        self,
        current: ProductSnapshot,
        previous: ProductSnapshot
    ):
        """檢查變化並發送通知"""
        # 價格變化 > 10%
        price_change = current.calculate_price_change_percentage(previous)
        if abs(price_change) >= 10:
            await self.notifier.send_price_alert(
                product_id=current.product_id,
                old_price=previous.price,
                new_price=current.price,
                change_percentage=price_change
            )

        # BSR 變化 > 30%
        bsr_change = current.calculate_bsr_change_percentage(previous)
        if abs(bsr_change) >= 30:
            await self.notifier.send_bsr_alert(
                product_id=current.product_id,
                old_bsr=previous.bsr_sub,
                new_bsr=current.bsr_sub,
                change_percentage=bsr_change
            )


# use_cases/product/get_product_history.py
from typing import List
from domain.entities.product import ProductSnapshot
from domain.repositories.product_repository import SnapshotRepository

class GetProductHistoryUseCase:
    """查詢產品歷史資料 Use Case"""

    def __init__(self, snapshot_repository: SnapshotRepository):
        self.repository = snapshot_repository

    async def execute(self, product_id: str, limit: int = 30) -> List[ProductSnapshot]:
        """取得產品最近 N 天的快照"""
        return await self.repository.find_by_product_id(product_id, limit)


# use_cases/product/batch_update_snapshots.py
from typing import List
from domain.repositories.product_repository import ProductRepository
from use_cases.product.update_product_snapshot import UpdateProductSnapshotUseCase

class BatchUpdateSnapshotsUseCase:
    """批次更新產品快照 Use Case"""

    def __init__(
        self,
        product_repository: ProductRepository,
        update_snapshot_use_case: UpdateProductSnapshotUseCase
    ):
        self.product_repo = product_repository
        self.update_use_case = update_snapshot_use_case

    async def execute(self) -> dict:
        """
        批次更新所有啟用產品的快照

        適用於 Celery Beat 每日排程任務
        """
        products = await self.product_repo.find_all_active()

        results = {
            "total": len(products),
            "success": 0,
            "failed": 0,
            "errors": []
        }

        for product in products:
            try:
                await self.update_use_case.execute(product.id)
                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "product_id": product.id,
                    "asin": product.asin,
                    "error": str(e)
                })

        return results
```

#### Ports（介面定義）

```python
# use_cases/ports/scraper_port.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class ScrapedProductData:
    """爬蟲回傳的產品資料"""
    asin: str
    title: str
    category: str
    price: Optional[Decimal]
    currency: str
    bsr_main: Optional[int]
    bsr_sub: Optional[int]
    rating: Optional[float]
    review_count: Optional[int]
    buybox_price: Optional[Decimal]

class ScraperPort(ABC):
    """爬蟲服務介面"""

    @abstractmethod
    async def scrape_product(self, asin: str) -> ScrapedProductData:
        """爬取產品資料"""
        pass


# use_cases/ports/notification_port.py
from abc import ABC, abstractmethod
from decimal import Decimal

class NotificationPort(ABC):
    """通知服務介面"""

    @abstractmethod
    async def send_price_alert(
        self,
        product_id: str,
        old_price: Decimal,
        new_price: Decimal,
        change_percentage: float
    ):
        """發送價格變動警報"""
        pass

    @abstractmethod
    async def send_bsr_alert(
        self,
        product_id: str,
        old_bsr: int,
        new_bsr: int,
        change_percentage: float
    ):
        """發送 BSR 變動警報"""
        pass


# use_cases/ports/cache_port.py
from abc import ABC, abstractmethod
from typing import Optional

class CachePort(ABC):
    """快取服務介面"""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """取得快取"""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int):
        """設定快取"""
        pass

    @abstractmethod
    async def delete(self, key: str):
        """刪除快取"""
        pass
```

### 3. Adapter Layer（介面適配層）

#### API Endpoints

```python
# adapters/api/v1/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from adapters.api.dependencies import (
    TrackProductUseCaseDep,
    UpdateProductSnapshotUseCaseDep,
    GetProductHistoryUseCaseDep
)
from adapters.api.schemas.product import (
    CreateProductRequest,
    ProductResponse,
    SnapshotResponse
)
from adapters.api.schemas.response import APIResponse

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=APIResponse[ProductResponse], status_code=201)
async def track_product(
    request: CreateProductRequest,
    use_case: TrackProductUseCaseDep
):
    """追蹤新產品"""
    product = await use_case.execute(
        asin=request.asin,
        user_id=request.user_id
    )
    return APIResponse(
        success=True,
        data=ProductResponse.from_entity(product)
    )

@router.post("/{product_id}/snapshots", response_model=APIResponse[SnapshotResponse])
async def update_snapshot(
    product_id: str,
    use_case: UpdateProductSnapshotUseCaseDep
):
    """手動更新產品快照"""
    snapshot = await use_case.execute(product_id=product_id)
    return APIResponse(
        success=True,
        data=SnapshotResponse.from_entity(snapshot)
    )

@router.get("/{product_id}/history", response_model=APIResponse[List[SnapshotResponse]])
async def get_product_history(
    product_id: str,
    limit: int = 30,
    use_case: GetProductHistoryUseCaseDep
):
    """查詢產品歷史資料"""
    snapshots = await use_case.execute(product_id=product_id, limit=limit)
    return APIResponse(
        success=True,
        data=[SnapshotResponse.from_entity(s) for s in snapshots]
    )
```

#### External Adapters

```python
# adapters/external/apify_scraper.py
from use_cases.ports.scraper_port import ScraperPort, ScrapedProductData
from infrastructure.external.apify_client import ApifyClient
from use_cases.ports.cache_port import CachePort
import json

class ApifyScraper(ScraperPort):
    """Apify 爬蟲適配器"""

    def __init__(self, client: ApifyClient, cache: CachePort):
        self.client = client
        self.cache = cache

    async def scrape_product(self, asin: str) -> ScrapedProductData:
        """
        爬取產品資料

        1. 先檢查快取（24-48h TTL）
        2. 快取未命中則呼叫 Apify API
        3. 轉換資料格式為 Domain 物件
        4. 寫入快取
        """
        # 檢查快取
        cache_key = f"product:apify:{asin}"
        cached = await self.cache.get(cache_key)
        if cached:
            data = json.loads(cached)
            return self._parse_data(data)

        # 呼叫 Apify API
        raw_data = await self.client.scrape_amazon_product(asin)

        # 寫入快取（48 小時）
        await self.cache.set(cache_key, json.dumps(raw_data), ttl=48 * 3600)

        # 轉換資料
        return self._parse_data(raw_data)

    def _parse_data(self, data: dict) -> ScrapedProductData:
        """將 Apify 回傳的 JSON 轉換為 Domain 物件"""
        return ScrapedProductData(
            asin=data["asin"],
            title=data["title"],
            category=data.get("category", "Unknown"),
            price=Decimal(str(data["price"]["value"])) if data.get("price") else None,
            currency=data.get("price", {}).get("currency", "USD"),
            bsr_main=data.get("bsr", {}).get("main"),
            bsr_sub=data.get("bsr", {}).get("sub"),
            rating=data.get("rating"),
            review_count=data.get("reviewCount"),
            buybox_price=Decimal(str(data["buyboxPrice"])) if data.get("buyboxPrice") else None
        )
```

#### Repository Implementation

```python
# adapters/repositories/supabase_product_repo.py
from typing import List, Optional
from domain.entities.product import Product
from domain.repositories.product_repository import ProductRepository
from infrastructure.database.supabase import SupabaseClient

class SupabaseProductRepository(ProductRepository):
    """Supabase 產品倉儲實作"""

    def __init__(self, client: SupabaseClient):
        self.client = client

    async def save(self, product: Product) -> Product:
        """儲存產品"""
        data = {
            "id": product.id,
            "asin": product.asin,
            "title": product.title,
            "category": product.category,
            "user_id": product.user_id,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }
        result = await self.client.table("products").insert(data).execute()
        return product

    async def find_by_asin(self, asin: str) -> Optional[Product]:
        """依 ASIN 查詢"""
        result = await self.client.table("products")\
            .select("*")\
            .eq("asin", asin)\
            .single()\
            .execute()

        if not result.data:
            return None

        return self._to_entity(result.data)

    async def find_all_active(self) -> List[Product]:
        """查詢所有啟用的產品"""
        result = await self.client.table("products")\
            .select("*")\
            .eq("is_active", True)\
            .execute()

        return [self._to_entity(row) for row in result.data]

    def _to_entity(self, row: dict) -> Product:
        """將資料庫 row 轉換為 Entity"""
        return Product(
            id=row["id"],
            asin=row["asin"],
            title=row["title"],
            category=row["category"],
            user_id=row["user_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )
```

### 4. Infrastructure Layer（基礎設施層）

#### Celery Tasks

```python
# infrastructure/tasks/product_tasks.py
from celery import Celery
from adapters.api.dependencies import get_batch_update_use_case

celery_app = Celery("transbiz")

@celery_app.task(name="daily_update_snapshots")
async def daily_update_snapshots():
    """每日更新所有產品快照"""
    use_case = get_batch_update_use_case()
    results = await use_case.execute()

    # 記錄結果
    logger.info(f"Batch update completed: {results}")
    return results


# infrastructure/tasks/celery_beat_config.py
from celery.schedules import crontab

beat_schedule = {
    'daily-update-snapshots': {
        'task': 'daily_update_snapshots',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨 2:00
    },
}
```

## 資料庫設計

### products 表

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asin VARCHAR(10) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    category VARCHAR(255),
    user_id UUID NOT NULL REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_products_asin ON products(asin);
CREATE INDEX idx_products_user_id ON products(user_id);
CREATE INDEX idx_products_is_active ON products(is_active);
```

### product_snapshots 表

```sql
CREATE TABLE product_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    asin VARCHAR(10) NOT NULL,

    -- 追蹤項目
    price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    bsr_main INTEGER,
    bsr_sub INTEGER,
    rating DECIMAL(2, 1),
    review_count INTEGER,
    buybox_price DECIMAL(10, 2),

    -- 元資料
    scraped_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_snapshots_product_id ON product_snapshots(product_id);
CREATE INDEX idx_snapshots_scraped_at ON product_snapshots(scraped_at DESC);
CREATE INDEX idx_snapshots_product_scraped ON product_snapshots(product_id, scraped_at DESC);
```

### change_alerts 表

```sql
CREATE TABLE change_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,  -- PRICE_CHANGE, BSR_CHANGE
    change_percentage DECIMAL(5, 2) NOT NULL,
    old_value DECIMAL(10, 2),
    new_value DECIMAL(10, 2),
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notified BOOLEAN DEFAULT FALSE,
    notified_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_alerts_product_id ON change_alerts(product_id);
CREATE INDEX idx_alerts_triggered_at ON change_alerts(triggered_at DESC);
CREATE INDEX idx_alerts_notified ON change_alerts(notified);
```

## 實作步驟

### Phase 1: 基礎架構（1-2 天）

1. **建立目錄結構**
   - 按照 Clean Architecture 分層
   - 建立各層的 `__init__.py`

2. **實作 Domain Layer**
   - ✅ 定義 Entity（Product, ProductSnapshot, ChangeAlert）
   - ✅ 定義 Value Object（Price, BSR）
   - ✅ 定義 Repository Interface

3. **建立資料庫 Schema**
   - 在 Supabase 建立表格
   - 設定 Index

4. **設定環境變數**
   - Supabase credentials
   - Apify API key
   - Redis URL

### Phase 2: Use Case 實作（2-3 天）

1. **實作核心 Use Cases**
   - ✅ TrackProductUseCase
   - ✅ UpdateProductSnapshotUseCase
   - ✅ GetProductHistoryUseCase
   - ✅ BatchUpdateSnapshotsUseCase

2. **定義 Ports**
   - ✅ ScraperPort
   - ✅ NotificationPort
   - ✅ CachePort

### Phase 3: Adapter 實作（2-3 天）

1. **實作 External Adapters**
   - ApifyScraper（含快取邏輯）
   - EmailNotifier 或 LogNotifier

2. **實作 Repository**
   - SupabaseProductRepository
   - SupabaseSnapshotRepository

3. **實作 API Endpoints**
   - POST /api/v1/products（追蹤新產品）
   - POST /api/v1/products/{id}/snapshots（手動更新）
   - GET /api/v1/products/{id}/history（查詢歷史）

### Phase 4: Infrastructure 實作（1-2 天）

1. **設定 Celery**
   - 配置 Celery app
   - 實作背景任務
   - 設定 Celery Beat 排程

2. **設定 Redis**
   - 連線配置
   - 快取策略實作

### Phase 5: 測試與優化（1-2 天）

1. **單元測試**
   - Domain Layer 測試（Entity 驗證邏輯）
   - Use Case 測試（使用 Mock）

2. **整合測試**
   - API Endpoint 測試
   - Apify 爬蟲測試（真實 API）

3. **效能測試**
   - 批次更新 10-20 個產品
   - 快取命中率驗證

## 討論問題

### Q1: Apify Actor 選擇

**選項 A**: 使用現成的 "Amazon Product Details" Actor

- 優勢：快速開始，功能完整
- 劣勢：可能包含不需要的資料

**選項 B**: 使用多個 Actor 組合

- "Amazon Product Details" + "Amazon Reviews"
- 優勢：資料更完整
- 劣勢：複雜度較高，成本較高

**你的偏好？**

### Q2: 快取策略

**Repository 層快取 vs Scraper 層快取**

目前設計：快取在 `ApifyScraper` 內（Adapter 層）

**優勢**：

- 對 Use Case 透明
- 減少 Apify API 呼叫
- 快取 TTL 可彈性調整

**你是否同意此設計？**

### Q3: 通知機制 ✅ 已決策：介面分離，初期 Log 實作

**決策**：使用 Port 介面分離，初期用 LogNotifier，未來可替換成 EmailNotifier

**實作設計**：

```python
# use_cases/ports/notification_port.py (介面定義)
class NotificationPort(ABC):
    @abstractmethod
    async def send_price_alert(self, product_id, old_price, new_price, change_percentage):
        pass

    @abstractmethod
    async def send_bsr_alert(self, product_id, old_bsr, new_bsr, change_percentage):
        pass


# adapters/notifications/log_notifier.py (初期實作)
import logging

logger = logging.getLogger(__name__)

class LogNotifier(NotificationPort):
    """Console Log 通知實作 - Demo 使用"""

    async def send_price_alert(self, product_id, old_price, new_price, change_percentage):
        logger.warning(
            f"⚠️ PRICE ALERT: Product {product_id} "
            f"changed {change_percentage:.2f}% "
            f"({old_price} → {new_price})"
        )

    async def send_bsr_alert(self, product_id, old_bsr, new_bsr, change_percentage):
        logger.warning(
            f"📊 BSR ALERT: Product {product_id} "
            f"changed {change_percentage:.2f}% "
            f"({old_bsr} → {new_bsr})"
        )


# adapters/notifications/email_notifier.py (未來實作)
class EmailNotifier(NotificationPort):
    """Email 通知實作 - 正式環境使用"""

    def __init__(self, smtp_client):
        self.smtp = smtp_client

    async def send_price_alert(self, product_id, old_price, new_price, change_percentage):
        # 實作 Email 發送邏輯
        await self.smtp.send_email(
            subject=f"Price Alert: {change_percentage:.1f}% change",
            body=f"Product {product_id} price changed from {old_price} to {new_price}"
        )
```

**切換方式（在 dependencies.py）**：

```python
# adapters/api/dependencies.py
def get_notifier() -> NotificationPort:
    # 初期：使用 LogNotifier
    return LogNotifier()

    # 未來：切換成 EmailNotifier（只需改這一行）
    # smtp_client = get_smtp_client()
    # return EmailNotifier(smtp_client)
```

**優勢**：

- ✅ Use Case 不依賴具體實作
- ✅ 初期快速驗證功能（不用設定 Email）
- ✅ 未來升級只需實作新 Adapter，不用改 Use Case
- ✅ 可同時支援多種通知方式（Log + Email）

### Q4: 批次更新策略 ✅ 已決策：Concurrent 並發更新

**決策**：使用 asyncio.gather 並發更新，支援 1000+ 產品

**實作設計**：

```python
# use_cases/product/batch_update_snapshots.py
import asyncio
from typing import Dict, List

class BatchUpdateSnapshotsUseCase:
    async def execute(self) -> Dict:
        """並發更新所有產品"""
        products = await self.product_repo.find_all_active()

        # 並發執行所有更新任務
        tasks = [
            self._update_single_product(product.id)
            for product in products
        ]

        # gather 會同時執行所有任務，return_exceptions=True 確保不會因單一失敗而中斷
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 統計結果
        return self._aggregate_results(products, results)

    async def _update_single_product(self, product_id: str):
        """更新單一產品（含錯誤處理）"""
        try:
            return await self.update_use_case.execute(product_id)
        except Exception as e:
            logger.error(f"Failed to update {product_id}: {e}")
            raise

    def _aggregate_results(self, products, results):
        """統計成功/失敗數量"""
        success = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - success
        return {
            "total": len(products),
            "success": success,
            "failed": failed,
            "errors": [str(r) for r in results if isinstance(r, Exception)]
        }
```

**優勢**：

- ✅ 1000 個產品可在幾分鐘內完成（vs 逐一更新需數小時）
- ✅ 單一產品失敗不影響其他產品
- ✅ 可設定並發數量限制（使用 semaphore）避免 API rate limit

## 下一步

1. **確認上述 Q1-Q4 的技術決策**
2. 開始實作 Phase 1（Domain Layer + DB Schema）
3. 測試基本的 CRUD 操作
4. 實作第一個完整流程（追蹤產品 → 爬取資料 → 儲存快照）

---

**記錄日期**：2025-10-08
**參考文件**：plan1.md, plan2.md, Issues.md
