class ExponentialBackoff:
    def __init__(self, base_delay: int = 1, max_delay: int = 60):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_count = 0

    def next_delay(self) -> int:
        delay = min(self.base_delay * (2 ** self.retry_count), self.max_delay)
        self.retry_count += 1
        return delay

    def reset(self) -> None:
        self.retry_count = 0
