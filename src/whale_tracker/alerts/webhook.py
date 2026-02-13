import aiohttp

from whale_tracker.alerts.base import Alert, AlertHandler


class WebhookHandler(AlertHandler):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, alert: Alert) -> None:
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=alert.__dict__)
