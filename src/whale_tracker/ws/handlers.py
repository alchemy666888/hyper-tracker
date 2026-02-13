from whale_tracker.events.normalizer import NormalizedEvent


async def handle_event(event: NormalizedEvent) -> None:
    _ = event
