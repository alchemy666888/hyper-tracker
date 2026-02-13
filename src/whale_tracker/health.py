from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException

app = FastAPI()


class HealthChecker:
    def __init__(self, manager, db):
        self.ws_manager = manager
        self.db = db

    async def check(self) -> dict:
        ws_ok = self.ws_manager.is_connected()
        db_ok = await self.db.healthcheck()
        return {
            "status": "healthy" if ws_ok and db_ok else "degraded",
            "websocket": "connected" if ws_ok else "disconnected",
            "database": "ok" if db_ok else "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@app.get("/health")
async def health(checker: HealthChecker = Depends()):
    status = await checker.check()
    if status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=status)
    return status
