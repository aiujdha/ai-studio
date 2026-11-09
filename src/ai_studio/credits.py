"""Quota extension contract; the local ledger is implemented in runtime.py."""

from typing import Protocol


class CreditLedger(Protocol):
    async def reserve(self, user_id: str, run_id: str, estimated: int) -> None:
        ...

    async def settle(self, run_id: str, actual: int) -> None:
        ...

    async def release(self, run_id: str) -> None:
        ...
