class BackfillService:
    def __init__(self, repo, rest_client, state_machine):
        self.repo = repo
        self.rest_client = rest_client
        self.state_machine = state_machine

    async def backfill_since_last_fill(self, wallet: str) -> None:
        last_fill = await self.repo.get_last_fill_timestamp(wallet)
        fills = await self.rest_client.get_user_fills(wallet, since=last_fill)
        for fill in fills:
            _ = fill
