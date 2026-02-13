import asyncio

import pytest

from whale_tracker.config import Settings
from whale_tracker.ws.manager import WebSocketManager


def test_websocket_reconnect_with_exponential_backoff(monkeypatch):
    async def run():
        manager = WebSocketManager(Settings(max_ws_failures=3))
        calls = {"count": 0}

        async def fake_connect(url):
            _ = url
            calls["count"] += 1
            raise RuntimeError("network down")

        async def fake_sleep(_):
            return None

        monkeypatch.setattr("whale_tracker.ws.manager.websockets.connect", fake_connect)
        monkeypatch.setattr("whale_tracker.ws.manager.asyncio.sleep", fake_sleep)

        with pytest.raises(RuntimeError, match="circuit breaker open"):
            await manager.connect()

        assert calls["count"] == 3

    asyncio.run(run())
