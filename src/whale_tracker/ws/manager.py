import asyncio
import json
from collections.abc import AsyncIterator

from whale_tracker.config import Settings
from whale_tracker.events.normalizer import EventNormalizer, NormalizedEvent
from whale_tracker.logging import logger
from whale_tracker.metrics import Metrics
from whale_tracker.ws.subscriptions import SubscriptionManager


class _Websockets:
    async def connect(self, _url: str):
        raise RuntimeError("websocket client not configured")


websockets = _Websockets()


class WebSocketManager:
    def __init__(self, config: Settings, normalizer: EventNormalizer | None = None) -> None:
        self.config = config
        self.normalizer = normalizer or EventNormalizer()
        self.subscriptions = SubscriptionManager()
        self._ws = None
        self._failures = 0
        self._connected = False
        self._stop = False

    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        while not self._stop:
            try:
                self._ws = await websockets.connect(self.config.ws_url)
                self._connected = True
                self._failures = 0
                await self.subscriptions.resubscribe_all(self.subscribe)
                return
            except Exception as exc:
                self._failures += 1
                if self._failures >= self.config.max_ws_failures:
                    raise RuntimeError("circuit breaker open") from exc
                delay = min(2 ** self._failures, 60)
                logger.warning("ws_connect_failed failure_count=%s delay=%s", self._failures, delay)
                Metrics.ws_reconnections_total.inc()
                await asyncio.sleep(delay)

    async def subscribe(self, channel: str, **filters) -> None:
        if not self._ws:
            raise RuntimeError("websocket is not connected")
        payload = {"method": "subscribe", "subscription": {"type": channel, **filters}}
        await self._ws.send(json.dumps(payload))

    async def _heartbeat(self) -> None:
        if not self._ws:
            return
        pong = await self._ws.ping()
        await asyncio.wait_for(pong, timeout=self.config.pong_timeout_seconds)

    async def listen(self) -> AsyncIterator[NormalizedEvent]:
        while not self._stop:
            if not self._ws or not self._connected:
                await self.connect()
            assert self._ws is not None
            try:
                raw_message = await asyncio.wait_for(self._ws.recv(), timeout=self.config.heartbeat_interval_seconds)
                raw_event = json.loads(raw_message)
                event = self.normalizer.normalize(raw_event)
                if self.normalizer.is_duplicate(event):
                    continue
                Metrics.ws_events_total.labels(event.event_type).inc()
                yield event
            except asyncio.TimeoutError:
                await self._heartbeat()
            except Exception:
                self._connected = False
                if self._ws:
                    await self._ws.close()

    async def disconnect(self) -> None:
        self._stop = True
        if self._ws:
            await self._ws.close()
        self._connected = False
