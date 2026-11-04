"""Asset and source-run boundary; no files or object storage are provided."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Asset:
    id: str
    owner_id: str
    source_run_id: str
    media_type: str
    storage_key: str


class AssetStore(Protocol):
    async def register(self, asset: Asset) -> None:
        ...

    async def list_for_run(self, run_id: str) -> tuple[Asset, ...]:
        ...
