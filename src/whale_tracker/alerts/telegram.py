from whale_tracker.alerts.base import Alert, AlertHandler


class TelegramHandler(AlertHandler):
    def __init__(self, bot, chat_id: str):
        self.bot = bot
        self.chat_id = chat_id

    async def send(self, alert: Alert) -> None:
        text = f"🐳 {alert.title}\n{alert.message}"
        await self.bot.send_message(self.chat_id, text)
