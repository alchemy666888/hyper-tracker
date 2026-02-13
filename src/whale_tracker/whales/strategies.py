from abc import ABC, abstractmethod

from whale_tracker.positions.models import PositionState


class WhaleDetectionStrategy(ABC):
    @abstractmethod
    async def classify(self, position: PositionState) -> bool:
        ...

    @abstractmethod
    async def get_confidence(self, position: PositionState) -> float:
        ...
