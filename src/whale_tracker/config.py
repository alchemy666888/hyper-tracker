from dataclasses import dataclass


@dataclass
class Settings:
    ws_url: str = "wss://api.hyperliquid.xyz/ws"
    rest_url: str = "https://api.hyperliquid.xyz"
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/whales"
    heartbeat_interval_seconds: int = 30
    pong_timeout_seconds: int = 10
    max_ws_failures: int = 10
    whale_notional_threshold_usd: float = 100_000
    whale_volume_24h_threshold_usd: float = 1_000_000
