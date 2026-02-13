from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Alert:
    severity: AlertSeverity
    title: str
    message: str
    data: dict
    timestamp: datetime


class AlertHandler(ABC):
    @abstractmethod
    async def send(self, alert: Alert) -> None:
        pass
