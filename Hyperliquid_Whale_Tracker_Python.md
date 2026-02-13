# Hyperliquid Whale Tracker — Python Development Plan

## Core Philosophy

This is not just a data ingestion system.

This is a **real-time whale radar** for Hyperliquid, built with Python's async ecosystem.

We are building:

- ⚡ Ultra-low-latency with `asyncio` + native WebSocket
- 🧠 State-aware with Redis hot-cache
- 🔧 Self-healing with exponential backoff and circuit breakers
- 📈 Position-lifecycle intelligent with deterministic state machines
- 🐳 Whale-detection native with pluggable detection engines

The system should feel:
- Calm under chaos
- Deterministic and testable
- Production-ready from day one
- Horizontally scalable with minimal infrastructure

---

## Tech Stack (Python)

### Core Runtime
- **Python 3.11+** (async/await, type hints, match statements)
- **asyncio** (event loop, concurrency)
- **aiohttp** (async HTTP client)
- **websockets** (async WebSocket client)

### Data Layer
- **TimescaleDB** (PostgreSQL extension for time-series)
- **SQLAlchemy 2.0** (async ORM with `asyncpg`)
- **asyncpg** (fast async PostgreSQL driver)
- **redis-py** (async support via `aioredis`)
- **Pydantic v2** (data validation, serialization)

### State Management
- **Redis** (in-memory state cache)
- **dataclasses** (lightweight state objects)
- **frozen dataclasses** (immutable position snapshots)

### Observability
- **structlog** (structured JSON logging)
- **prometheus-client** (metrics)
- **opentelemetry** (optional: distributed tracing)

### Testing & Quality
- **pytest** (unit/integration testing)
- **pytest-asyncio** (async test fixtures)
- **hypothesis** (property-based testing for state machines)
- **pyright** (static type checking)

### Deployment
- **Docker** (containerization)
- **docker-compose** (local dev orchestration)
- **Kubernetes** (optional: production scaling)
- **systemd** (Linux process management)

---

## Project Structure

```
hyperliquid-whale-tracker/
├── src/
│   ├── whale_tracker/
│   │   ├── __init__.py
│   │   ├── main.py                    # Entry point
│   │   ├── config.py                  # Settings + env vars
│   │   ├── logging.py                 # Structured logging
│   │   │
│   │   ├── ws/
│   │   │   ├── manager.py             # WebSocket lifecycle
│   │   │   ├── subscriptions.py       # Subscription logic
│   │   │   └── handlers.py            # Event handlers
│   │   │
│   │   ├── events/
│   │   │   ├── models.py              # Event dataclasses
│   │   │   ├── normalizer.py          # Event normalization
│   │   │   └── streaming.py           # Event streaming interface
│   │   │
│   │   ├── positions/
│   │   │   ├── models.py              # Position state (frozen dataclass)
│   │   │   ├── state_machine.py       # Deterministic state transitions
│   │   │   ├── lifecycle.py           # Position lifecycle tracking
│   │   │   └── cache.py               # Redis cache layer
│   │   │
│   │   ├── whales/
│   │   │   ├── detector.py            # Whale classification engine
│   │   │   ├── registry.py            # Dynamic whale registry
│   │   │   ├── strategies.py          # Detection strategies (pluggable)
│   │   │   └── filters.py             # Threshold-based filters
│   │   │
│   │   ├── persistence/
│   │   │   ├── db.py                  # SQLAlchemy engine + session factory
│   │   │   ├── models.py              # ORM models
│   │   │   ├── migrations/            # Alembic migrations
│   │   │   └── repository.py          # Data access layer
│   │   │
│   │   ├── rest/
│   │   │   ├── client.py              # Hyperliquid REST client
│   │   │   ├── backfill.py            # Backfill + recovery logic
│   │   │   └── rate_limiter.py        # Request rate limiting
│   │   │
│   │   ├── alerts/
│   │   │   ├── base.py                # Abstract alert handler
│   │   │   ├── telegram.py            # Telegram notifications
│   │   │   ├── webhook.py             # Generic webhook
│   │   │   └── rules.py               # Alert trigger rules
│   │   │
│   │   ├── metrics.py                 # Prometheus metrics
│   │   ├── health.py                  # Health check endpoints
│   │   └── types.py                   # Shared type definitions
│   │
│   └── tests/
│       ├── unit/
│       │   ├── test_state_machine.py
│       │   ├── test_whale_detector.py
│       │   └── test_position_lifecycle.py
│       │
│       ├── integration/
│       │   ├── test_ws_manager.py
│       │   ├── test_e2e_position_flow.py
│       │   └── fixtures.py
│       │
│       └── conftest.py
│
├── docker-compose.yml                 # Local dev environment
├── Dockerfile                         # Production image
├── requirements.txt                   # Python dependencies
├── requirements-dev.txt               # Dev-only dependencies
├── pyproject.toml                     # Project metadata
├── pytest.ini                         # Pytest configuration
├── .env.example                       # Environment template
└── README.md
```

---

## Development Phases (Python-Focused)

---

## PHASE 1 — Foundation (Event Layer)

### 🎯 Goal
Build reliable real-time ingestion from Hyperliquid using async Python.

### Scope

#### 1. WebSocket Manager (`ws/manager.py`)

```python
class WebSocketManager:
    """Manages persistent WebSocket connection with auto-reconnect."""
    
    async def connect(self) -> None:
        """Establish WebSocket with exponential backoff."""
    
    async def subscribe(self, channel: str, **filters) -> None:
        """Subscribe to Hyperliquid channels."""
    
    async def listen(self) -> AsyncIterator[Event]:
        """Stream incoming events with automatic reconnection."""
    
    async def disconnect(self) -> None:
        """Graceful shutdown."""
```

**Implementation Details:**
- Use `websockets` library with `asyncio`
- Exponential backoff: `min(2^retry, 60)` seconds
- Heartbeat: Send ping every 30s, close if pong not received in 10s
- Auto-resubscribe on reconnect using subscription cache
- Circuit breaker: Stop retrying after 10 consecutive failures

#### 2. Subscription Manager (`ws/subscriptions.py`)

```python
class SubscriptionManager:
    """Manages active subscriptions."""
    
    subscriptions: dict[str, Subscription]
    
    def subscribe_user_events(self, wallet: str) -> None:
        """Subscribe to user-specific events."""
    
    def subscribe_liquidations(self, market: str = "*") -> None:
        """Subscribe to liquidation stream."""
    
    def subscribe_funding(self, market: str) -> None:
        """Subscribe to funding rate updates."""
    
    async def resubscribe_all(self) -> None:
        """Replay all subscriptions on reconnect."""
```

#### 3. Event Normalizer (`events/normalizer.py`)

```python
@dataclass
class NormalizedEvent:
    """Universal event format."""
    event_type: str  # 'fill', 'funding', 'liquidation'
    wallet: str
    market: str
    timestamp: datetime
    data: dict
    idempotency_key: str  # Deduplication key

class EventNormalizer:
    """Convert Hyperliquid events to standard format."""
    
    def normalize(self, raw_event: dict) -> NormalizedEvent:
        """Parse + validate raw WebSocket event."""
    
    def get_idempotency_key(self, event: dict) -> str:
        """Extract unique event identifier."""
```

**Deduplication Strategy:**
- Store `idempotency_key` in memory (in-memory set, max 100k entries)
- Clean old keys after 5 minutes
- Skip duplicate events silently

#### 4. REST Fallback (`rest/client.py`)

```python
class HyperliquidRESTClient:
    """Async REST client for backfill + recovery."""
    
    async def get_user_fills(
        self, 
        wallet: str, 
        since: datetime | None = None
    ) -> list[Fill]:
        """Fetch historical fills with optional time filter."""
    
    async def get_user_state(self, wallet: str) -> UserState:
        """Get current account state (positions, balances)."""
    
    async def get_funding_history(
        self, 
        market: str, 
        limit: int = 1000
    ) -> list[FundingEvent]:
        """Fetch funding history for market."""
```

### Deliverables

- ✅ Stable async WebSocket manager with auto-reconnect
- ✅ Event deduplication via idempotency keys
- ✅ Type-safe event models with Pydantic
- ✅ Comprehensive error handling and logging
- ✅ Unit tests for WebSocket lifecycle (pytest-asyncio)

### Testing Pattern (Phase 1)

```python
@pytest.mark.asyncio
async def test_websocket_reconnect_with_exponential_backoff():
    """Verify reconnection behavior."""
    manager = WebSocketManager(config)
    
    # Simulate network failure
    # Verify exponential backoff timing
    # Verify resubscription after reconnect
```

---

## PHASE 2 — Position Reconstruction Engine

### 🎯 Goal
Rebuild full position lifecycle from raw fills using deterministic state machines.

### Core Design

```python
from dataclasses import dataclass
from enum import Enum

class PositionDirection(str, Enum):
    LONG = "long"
    SHORT = "short"

@dataclass(frozen=True)
class PositionState:
    """Immutable position snapshot."""
    wallet: str
    market: str
    direction: PositionDirection
    size: float
    entry_price: float
    entry_timestamp: datetime
    
    accumulated_funding: float
    realized_pnl: float
    unrealized_pnl: float
    
    is_liquidated: bool = False
    
    def is_open(self) -> bool:
        return self.size > 0
```

### State Machine (`positions/state_machine.py`)

```python
class PositionStateMachine:
    """
    Deterministic state transitions.
    Input: Events (fills, funding, liquidation)
    Output: New immutable PositionState
    """
    
    def process_fill(
        self,
        state: PositionState,
        fill: Fill
    ) -> PositionState:
        """Handle fill event → new state."""
        # Case 1: Opening new position
        # Case 2: Increasing existing
        # Case 3: Partial close (realize PnL)
        # Case 4: Full close
        # Case 5: Flip (long → short)
        
    def process_funding(
        self,
        state: PositionState,
        funding: FundingEvent
    ) -> PositionState:
        """Add funding to realized PnL."""
    
    def process_liquidation(
        self,
        state: PositionState,
        liquidation: LiquidationEvent
    ) -> PositionState:
        """Force close + flag as liquidated."""
```

**Design Principles:**
- Pure functions: same input → same output
- No side effects (no DB writes in state machine)
- Immutable state (frozen dataclasses)
- All math deterministic (Decimal for precision)

### Position Cache (`positions/cache.py`)

```python
class PositionCache:
    """Redis-backed hot cache for live position state."""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def get_position(
        self,
        wallet: str,
        market: str
    ) -> PositionState | None:
        """Fetch from Redis (cache hit = <1ms)."""
    
    async def set_position(
        self,
        position: PositionState
    ) -> None:
        """Store in Redis with TTL (24h)."""
    
    async def invalidate(self, wallet: str, market: str) -> None:
        """Clear cached position."""
```

**Redis Key Pattern:**
```
position:{wallet}:{market} → JSON (PositionState)
wallet_positions:{wallet} → Set of all markets
```

### Lifecycle Tracker (`positions/lifecycle.py`)

```python
class PositionLifecycle:
    """Tracks complete position journey (open → close)."""
    
    async def record_open(self, position: PositionState) -> None:
        """Log position open (emit event)."""
    
    async def record_update(
        self,
        old_state: PositionState,
        new_state: PositionState
    ) -> None:
        """Track state changes."""
    
    async def record_close(self, position: PositionState) -> None:
        """Log final position state before close."""
    
    def emit_position_event(
        self,
        event_type: str,  # 'opened', 'increased', 'decreased', 'closed', 'liquidated'
        position: PositionState,
        metadata: dict | None = None
    ) -> PositionEvent:
        """Create typed event for downstream."""
```

### Deliverables

- ✅ Deterministic state machine (100% test coverage)
- ✅ Frozen dataclass states for immutability
- ✅ Redis cache layer for sub-millisecond lookups
- ✅ Property-based testing with Hypothesis (edge cases)
- ✅ Position lifecycle events emitted

### Testing Pattern (Phase 2)

```python
def test_position_state_machine_full_lifecycle():
    """Test: open → increase → partial close → flip → close."""
    machine = PositionStateMachine()
    
    # State 0: Empty
    state = PositionState.empty(wallet="0xabc", market="BTC")
    
    # Event 1: Open long 1 BTC at $45k
    state = machine.process_fill(state, Fill(...))
    assert state.direction == PositionDirection.LONG
    assert state.size == 1.0
    
    # Event 2: Add 0.5 BTC at $45.5k
    state = machine.process_fill(state, Fill(...))
    assert state.size == 1.5
    assert state.entry_price == weighted_avg(...)
    
    # Event 3: Partial close (sell 1 BTC)
    state = machine.process_fill(state, Fill(...))
    assert state.size == 0.5
    assert state.realized_pnl > 0
    
    # Verify math deterministically

@given(fills=st.lists(fill_strategy()))
def test_state_machine_commutative_fills(fills):
    """Property: Reordering fills maintains consistent final state."""
    # (Note: Only if fills are non-overlapping)
```

---

## PHASE 3 — Whale Detection Engine

### 🎯 Goal
Filter noise. Track only meaningful capital with pluggable detection strategies.

### Strategy Interface (`whales/strategies.py`)

```python
from abc import ABC, abstractmethod

class WhaleDetectionStrategy(ABC):
    """Abstract base for whale detection."""
    
    @abstractmethod
    async def classify(
        self,
        position: PositionState
    ) -> bool:
        """Return True if position qualifies as whale."""
        ...
    
    @abstractmethod
    async def get_confidence(self, position: PositionState) -> float:
        """Return 0.0-1.0 confidence score."""
        ...
```

### Strategy A — Threshold-Based (`whales/filters.py`)

```python
class ThresholdStrategy(WhaleDetectionStrategy):
    """Simple notional size + 24h volume filters."""
    
    def __init__(
        self,
        notional_threshold_usd: float = 100_000,
        volume_24h_threshold_usd: float = 1_000_000
    ):
        self.notional_threshold = notional_threshold_usd
        self.volume_24h_threshold = volume_24h_threshold_usd
    
    async def classify(self, position: PositionState) -> bool:
        notional = abs(position.size * position.entry_price)
        volume_24h = await self.get_market_volume_24h(position.market)
        
        return (notional > self.notional_threshold or 
                volume_24h > self.volume_24h_threshold)
```

### Strategy B — Registry-Based (`whales/registry.py`)

```python
class WhaleRegistry:
    """Dynamic registry of known whale wallets."""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def add_whale(self, wallet: str, reason: str) -> None:
        """Register a whale."""
    
    async def is_whale(self, wallet: str) -> bool:
        """Check if wallet in registry."""
    
    async def auto_update_top_wallets(self) -> None:
        """
        Hourly job: Update registry with:
        - Top 100 by OI
        - Top 50 by realized PnL
        - Large liquidation contributors
        """
```

**Redis Storage:**
```
whales:registry → Set of wallet addresses
whale:metadata:{wallet} → {reason, added_at, last_active}
```

### Hybrid Detector (`whales/detector.py`)

```python
class HybridWhaleDetector:
    """Combines multiple strategies."""
    
    def __init__(
        self,
        strategies: list[WhaleDetectionStrategy],
        require_all: bool = False  # AND vs OR logic
    ):
        self.strategies = strategies
        self.require_all = require_all
    
    async def is_whale(self, position: PositionState) -> bool:
        """
        if require_all:
            return all(s.classify(position) for s in strategies)
        else:
            return any(s.classify(position) for s in strategies)
        """
    
    async def get_whale_score(self, position: PositionState) -> float:
        """Average confidence across strategies."""
        scores = [await s.get_confidence(position) for s in self.strategies]
        return sum(scores) / len(scores)
```

### Deliverables

- ✅ Abstract strategy interface
- ✅ Configurable threshold strategy (env vars)
- ✅ Redis-backed whale registry
- ✅ Hourly auto-update job for top wallets
- ✅ Hybrid detection with configurable logic
- ✅ Confidence scoring

---

## PHASE 4 — Storage Layer

### 🎯 Goal
Make everything queryable and scalable with TimescaleDB.

### Database Models (`persistence/models.py`)

```python
from sqlalchemy import Column, String, Float, DateTime, Boolean, DECIMAL, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class WhalePosition(Base):
    """ORM model for position lifecycle."""
    __tablename__ = "whale_positions"
    
    id = Column(Integer, primary_key=True)
    
    # Unique constraint for idempotency
    wallet_address = Column(String(66), nullable=False, index=True)
    market = Column(String(20), nullable=False, index=True)
    position_id = Column(String(100), nullable=False, unique=True)  # Idempotency key
    
    # Lifecycle
    open_datetime = Column(DateTime, nullable=False, index=True)
    close_datetime = Column(DateTime, nullable=True, index=True)
    
    # Entry/Exit
    direction = Column(String(10), nullable=False)  # 'long' or 'short'
    entry_price = Column(DECIMAL(20, 8), nullable=False)
    exit_price = Column(DECIMAL(20, 8), nullable=True)
    size = Column(Float, nullable=False)
    notional_usd = Column(Float, nullable=False)
    
    # P&L
    realized_pnl = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, nullable=True)
    funding_accumulated = Column(Float, default=0.0)
    
    # Status
    is_liquidated = Column(Boolean, default=False)
    is_whale = Column(Boolean, default=False, index=True)
    whale_confidence = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_wallet_market_timestamp', 'wallet_address', 'market', 'open_datetime'),
    )

class FundingEvent(Base):
    """Track funding rate changes."""
    __tablename__ = "funding_events"
    
    id = Column(Integer, primary_key=True)
    market = Column(String(20), nullable=False, index=True)
    wallet_address = Column(String(66), nullable=False, index=True)
    position_id = Column(String(100), nullable=False)
    
    funding_rate = Column(Float, nullable=False)
    funding_amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_market_timestamp', 'market', 'timestamp'),
    )
```

### Alembic Migrations

```bash
# Initialize (one-time)
alembic init -t async migrations

# Create migration
alembic revision --autogenerate -m "Create whale_positions table"

# Apply
alembic upgrade head
```

### Repository Pattern (`persistence/repository.py`)

```python
class PositionRepository:
    """Data access layer for positions."""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    async def save_position(
        self,
        position: PositionState,
        is_whale: bool,
        confidence: float
    ) -> None:
        """Insert or update position (idempotent)."""
        async with self.session_factory() as session:
            stmt = insert(WhalePosition).values(
                wallet_address=position.wallet,
                market=position.market,
                position_id=position.get_id(),  # Idempotency
                # ... other fields
            ).on_conflict_do_update(
                index_elements=['position_id'],
                set_={
                    'updated_at': datetime.utcnow(),
                    'is_whale': is_whale,
                    # ... update fields
                }
            )
            await session.execute(stmt)
            await session.commit()
    
    async def get_whale_positions(
        self,
        limit: int = 100,
        since: datetime | None = None
    ) -> list[WhalePosition]:
        """Query whale positions with filters."""
        async with self.session_factory() as session:
            stmt = select(WhalePosition).where(
                WhalePosition.is_whale == True
            )
            if since:
                stmt = stmt.where(WhalePosition.open_datetime >= since)
            stmt = stmt.order_by(WhalePosition.open_datetime.desc()).limit(limit)
            
            result = await session.execute(stmt)
            return result.scalars().all()
```

### Deliverables

- ✅ TimescaleDB schema with hypertable on `open_datetime`
- ✅ Alembic migrations for easy versioning
- ✅ SQLAlchemy 2.0 async ORM models
- ✅ Idempotent insert/update logic
- ✅ Repository pattern for clean data access

---

## PHASE 5 — Reliability & Self-Healing

### 🎯 Goal
Operate 24/7 without supervision.

### Reconnection Logic (`ws/manager.py`)

```python
class ReconnectionStrategy:
    """Exponential backoff with max retry guard."""
    
    def __init__(
        self,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        max_retries: int = 10
    ):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.retry_count = 0
    
    def next_delay(self) -> float:
        """Calculate next retry delay."""
        if self.retry_count >= self.max_retries:
            raise MaxRetriesExceeded()
        
        delay = min(self.initial_delay * (2 ** self.retry_count), self.max_delay)
        self.retry_count += 1
        return delay
    
    def reset(self) -> None:
        """Reset on successful connection."""
        self.retry_count = 0
```

### Backfill on Restart (`rest/backfill.py`)

```python
class BackfillService:
    """Recover missed fills after reconnect."""
    
    async def backfill_since_last_fill(self, wallet: str) -> None:
        """
        1. Query DB for last fill timestamp
        2. Fetch fills from REST API since then
        3. Process through state machine
        4. Persist to DB
        """
        last_fill = await self.repo.get_last_fill_timestamp(wallet)
        
        fills = await self.rest_client.get_user_fills(
            wallet,
            since=last_fill
        )
        
        for fill in fills:
            # Process through position state machine
            # Persist
            pass
```

### Observability (`metrics.py`)

```python
from prometheus_client import Counter, Histogram, Gauge

class Metrics:
    """Prometheus metrics."""
    
    ws_events_total = Counter(
        'ws_events_total',
        'Total WebSocket events received',
        ['event_type']
    )
    
    ws_reconnections_total = Counter(
        'ws_reconnections_total',
        'Total WebSocket reconnections'
    )
    
    position_updates_total = Counter(
        'position_updates_total',
        'Total position state updates',
        ['market']
    )
    
    whales_detected_total = Counter(
        'whales_detected_total',
        'Total whale positions detected'
    )
    
    backfill_lag_seconds = Gauge(
        'backfill_lag_seconds',
        'Seconds behind latest fills',
        ['wallet']
    )
    
    db_write_duration_seconds = Histogram(
        'db_write_duration_seconds',
        'Database write latency'
    )
```

### Structured Logging (`logging.py`)

```python
import structlog

# Configure
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

# Usage
logger.info("whale_position_opened", 
    wallet="0xabc...",
    market="BTC",
    size=5.0,
    notional_usd=225000
)
```

### Health Check (`health.py`)

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

class HealthChecker:
    def __init__(self, manager: WebSocketManager, db: Database):
        self.ws_manager = manager
        self.db = db
    
    async def check(self) -> dict:
        """Check system health."""
        ws_ok = self.ws_manager.is_connected()
        db_ok = await self.db.healthcheck()
        
        return {
            "status": "healthy" if ws_ok and db_ok else "degraded",
            "websocket": "connected" if ws_ok else "disconnected",
            "database": "ok" if db_ok else "error",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/health")
async def health(checker: HealthChecker = Depends()):
    health = await checker.check()
    if health["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health)
    return health
```

### Deliverables

- ✅ Exponential backoff reconnection strategy
- ✅ Automatic backfill on restart (within 24h window)
- ✅ Prometheus metrics for monitoring
- ✅ Structured JSON logging
- ✅ Health check endpoint

---

## PHASE 6 — Alerting

### 🎯 Goal
Real-time notifications for whale activity.

### Alert System (`alerts/`)

```python
from abc import ABC, abstractmethod
from enum import Enum

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class Alert:
    """Universal alert object."""
    severity: AlertSeverity
    title: str
    message: str
    data: dict
    timestamp: datetime

class AlertHandler(ABC):
    """Abstract alert delivery."""
    
    @abstractmethod
    async def send(self, alert: Alert) -> None:
        pass

class TelegramHandler(AlertHandler):
    """Send alerts to Telegram."""
    
    async def send(self, alert: Alert) -> None:
        text = f"🐳 {alert.title}\n{alert.message}"
        await self.bot.send_message(chat_id, text)

class WebhookHandler(AlertHandler):
    """Send alerts to custom webhook."""
    
    async def send(self, alert: Alert) -> None:
        await self.http_client.post(
            self.webhook_url,
            json=alert.model_dump()
        )
```

### Alert Rules (`alerts/rules.py`)

```python
class AlertRule(ABC):
    """Define alert trigger conditions."""
    
    @abstractmethod
    async def should_trigger(self, event: PositionEvent) -> Alert | None:
        pass

class WhaleOpenedRule(AlertRule):
    """Trigger on new whale position."""
    
    async def should_trigger(self, event: PositionEvent) -> Alert | None:
        if event.type != "opened":
            return None
        
        if event.position.is_whale and event.position.notional_usd > 500_000:
            return Alert(
                severity=AlertSeverity.WARNING,
                title=f"🐳 WHALE OPENED ${event.position.notional_usd:,.0f}",
                message=f"{event.position.wallet[:6]}... opened {event.position.size} {event.position.market} @ {event.position.entry_price}",
                data=event.position.model_dump()
            )

class WhaleLiquidatedRule(AlertRule):
    """Trigger on whale liquidation."""
    
    async def should_trigger(self, event: PositionEvent) -> Alert | None:
        if event.type != "liquidated":
            return None
        
        return Alert(
            severity=AlertSeverity.CRITICAL,
            title="💥 WHALE LIQUIDATED",
            message=f"{event.position.wallet[:6]}... liquidated {event.position.size} {event.position.market}",
            data=event.position.model_dump()
        )
```

### Deliverables

- ✅ Abstract alert handler interface
- ✅ Telegram + webhook implementations
- ✅ Configurable alert rules
- ✅ Rule evaluation on position events

---

## PHASE 7 — Deployment & Scaling

### 🎯 Goal
Production-ready orchestration.

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "whale_tracker.main"]
```

### Docker Compose (Local Dev)

```yaml
# docker-compose.yml
version: '3.9'

services:
  postgres:
    image: timescaledb/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: whale_tracker
      POSTGRES_USER: tracker
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  tracker:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://tracker:dev_password@postgres/whale_tracker
      REDIS_URL: redis://redis:6379
      HYPERLIQUID_WS: wss://api.hyperliquid.xyz/ws
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"  # Health check + metrics

volumes:
  postgres_data:
```

### Configuration (`config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost/whale_tracker"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # WebSocket
    hyperliquid_ws_url: str = "wss://api.hyperliquid.xyz/ws"
    
    # Whale Detection
    notional_threshold_usd: float = 100_000
    volume_24h_threshold_usd: float = 1_000_000
    
    # Alerts
    telegram_token: str | None = None
    telegram_chat_id: str | None = None
    webhook_url: str | None = None
    
    # Monitoring
    log_level: str = "INFO"
    metrics_port: int = 8000
    
    class Config:
        env_file = ".env"
```

### Systemd Unit (Linux)

```ini
# /etc/systemd/system/whale-tracker.service

[Unit]
Description=Hyperliquid Whale Tracker
After=network.target docker.service

[Service]
Type=simple
User=whale-tracker
WorkingDirectory=/opt/whale-tracker
ExecStart=/usr/bin/docker-compose up --no-build
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Horizontal Scaling

**Strategy:** Shard wallets across multiple tracker instances

```python
class WalletSharding:
    """Distribute wallet monitoring across instances."""
    
    def __init__(self, instance_id: int, total_instances: int):
        self.instance_id = instance_id
        self.total_instances = total_instances
    
    def owns_wallet(self, wallet: str) -> bool:
        """Consistent hash shard assignment."""
        wallet_hash = int(hashlib.md5(wallet.encode()).hexdigest(), 16)
        return (wallet_hash % self.total_instances) == self.instance_id
```

**Deployment:**
- Run 3-5 tracker instances behind a load balancer
- Each monitors 20% of wallets
- Shared Redis + PostgreSQL
- Health checks + auto-restart

### Deliverables

- ✅ Production Dockerfile
- ✅ Docker Compose for local dev
- ✅ Pydantic Settings for env config
- ✅ Systemd unit file
- ✅ Wallet sharding for horizontal scaling

---

## Testing Strategy

### Unit Tests (PHASE 1-3)

```bash
pytest src/tests/unit/test_state_machine.py -v
pytest src/tests/unit/test_whale_detector.py -v
pytest src/tests/unit/test_position_lifecycle.py -v
```

Coverage target: **>90%**

### Integration Tests (PHASE 4-5)

```bash
pytest src/tests/integration/ -v --asyncio-mode=auto
```

Uses fixtures:
- `async_postgres`: Local test DB
- `async_redis`: Local Redis
- `mock_ws`: Mocked WebSocket with recorded events

### End-to-End Flow Test

```python
@pytest.mark.asyncio
async def test_e2e_whale_detection_and_persistence():
    """Full flow: WebSocket → State Machine → DB → Alert."""
    
    # Setup
    tracker = WhaleTracker(test_config)
    
    # Simulate WebSocket events
    events = [
        Fill(wallet=whale1, size=5.0, price=45000),
        Fill(wallet=whale1, size=2.0, price=45500),
        LiquidationEvent(wallet=whale1, market="BTC")
    ]
    
    for event in events:
        await tracker.process_event(event)
    
    # Assertions
    position = await tracker.repo.get_position(whale1, "BTC")
    assert position.is_liquidated
    assert position.is_whale
    
    # Verify alert sent
    assert mock_alert_handler.called
```

### Performance Benchmarks

```python
@pytest.mark.benchmark
async def test_state_machine_throughput(benchmark):
    """1000 fills/sec → state updates."""
    machine = PositionStateMachine()
    
    fills = [synthetic_fill() for _ in range(1000)]
    
    async def process():
        state = PositionState.empty()
        for fill in fills:
            state = machine.process_fill(state, fill)
    
    result = benchmark(asyncio.run, process())
    # Target: <1ms for 1000 fills
```

---

## Development Workflow

### Local Setup

```bash
# Clone repo
git clone https://github.com/your-org/whale-tracker.git
cd whale-tracker

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Start services
docker-compose up -d

# Run tests
pytest src/tests/ -v

# Start tracker (dev mode)
python -m whale_tracker.main
```

### Code Quality

```bash
# Type checking
pyright src/

# Linting
ruff check src/ --fix

# Formatting
black src/

# All checks
make lint
```

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: timescaledb/timescaledb:latest-pg15
      redis:
        image: redis:7-alpine
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt
      - run: pytest src/tests/ --cov=src --cov-report=xml
      - run: pyright src/
      - uses: codecov/codecov-action@v3
```

---

## Operational Runbook

### Monitoring Dashboard (Grafana)

Key metrics to visualize:
- WebSocket connection status (uptime %)
- Event throughput (events/sec)
- Position update latency (p50, p95, p99)
- Whale count (active positions)
- Database write latency
- Cache hit rate

### On-Call Procedures

**Alert: WebSocket Disconnected**
1. Check Hyperliquid API status
2. Verify network connectivity
3. Check logs for handshake errors
4. Manual reconnect: `POST /restart`

**Alert: Backlog Growing**
1. Check database write latency
2. Check Redis connection
3. Scale to additional tracker instances
4. Check for data anomalies

**Alert: High PnL Position**
1. Verify position state
2. Check funding calculations
3. Cross-reference with Hyperliquid API
4. Alert relevant team

---

## Final Architecture Character

This system should feel:

- ⚙️ **Mechanical but elegant** — Async Python, type-safe, deterministic
- ⚡ **Real-time and reactive** — Sub-100ms event processing
- 🧠 **Stateful but rebuildable** — State machine can replay from fills
- 🐳 **Focused on capital movement** — Every event is material
- 🔥 **Built for market chaos** — Graceful degradation, self-healing

---

## End State Vision

```bash
$ python -m whale_tracker.main
2025-02-13 10:30:42 Starting Whale Tracker v1.0
2025-02-13 10:30:43 Connected to WebSocket
2025-02-13 10:30:44 Synced position cache (2,341 active positions)
2025-02-13 10:30:45 Ready for events

[... runs for months ...]

2025-03-15 14:22:31 🐳 WHALE OPENED $5,250,000 long BTC
2025-03-15 14:22:31   → wallet: 0x7f3a...
2025-03-15 14:22:31   → size: 125 contracts
2025-03-15 14:22:31   → entry: $42,000
2025-03-15 14:22:31 Alert sent to Telegram
2025-03-15 14:22:31 Position persisted to DB
```

**You press deploy.**

**It runs for months.**

**It never crashes.**

**And when a $2M BTC perp long opens…**

**You know within 200 milliseconds.**

That's the vibe.

---

## Success Criteria

- ✅ WebSocket uptime: >99.9%
- ✅ Event processing latency: <100ms (p95)
- ✅ False positive rate: <5% on whale detection
- ✅ Database consistency: 100% idempotency
- ✅ Deployment time: <5 minutes (blue-green)
- ✅ Recovery time: <2 minutes (auto-backfill)
- ✅ Scaling: Handle 1,000+ wallets on single instance

---

## References & Resources

- **Hyperliquid API Docs:** https://hyperliquid.gitbook.io/
- **asyncio Guide:** https://docs.python.org/3/library/asyncio.html
- **SQLAlchemy 2.0 Async:** https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **TimescaleDB Docs:** https://docs.timescale.com/
- **Prometheus Python Client:** https://github.com/prometheus/client_python
- **Pydantic v2:** https://docs.pydantic.dev/latest/

---

**Version:** 1.0  
**Last Updated:** February 2025  
**Status:** Ready for Implementation
