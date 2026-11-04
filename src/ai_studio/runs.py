"""Lifecycle vocabulary and service contract, not an executing state machine."""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class RunState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    RECOVERING = "recovering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass(frozen=True)
class Run:
    id: str
    user_id: str
    state: RunState


class RunService(Protocol):
    async def create(self, user_id: str, instruction: str) -> Run:
        ...

    async def get(self, run_id: str) -> Run:
        ...

    async def cancel(self, run_id: str) -> None:
        ...

    async def recover(self, run_id: str) -> Run:
        ...
