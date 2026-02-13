from collections.abc import AsyncIterator

from whale_tracker.events.normalizer import NormalizedEvent


class EventStream:
    def __init__(self, source: AsyncIterator[NormalizedEvent]):
        self.source = source

    async def __aiter__(self) -> AsyncIterator[NormalizedEvent]:
        async for event in self.source:
            yield event
