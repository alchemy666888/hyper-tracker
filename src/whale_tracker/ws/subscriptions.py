from dataclasses import dataclass, field


@dataclass(frozen=True)
class Subscription:
    channel: str
    filters: dict[str, str] = field(default_factory=dict)


class SubscriptionManager:
    def __init__(self) -> None:
        self.subscriptions: dict[str, Subscription] = {}

    def subscribe_user_events(self, wallet: str) -> None:
        self.subscriptions[f"user:{wallet}"] = Subscription(channel="user", filters={"user": wallet})

    def subscribe_liquidations(self, market: str = "*") -> None:
        self.subscriptions[f"liquidations:{market}"] = Subscription(channel="liquidations", filters={"coin": market})

    def subscribe_funding(self, market: str) -> None:
        self.subscriptions[f"funding:{market}"] = Subscription(channel="funding", filters={"coin": market})

    async def resubscribe_all(self, callback) -> None:
        for sub in self.subscriptions.values():
            await callback(sub.channel, **sub.filters)
