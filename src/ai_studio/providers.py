"""Image/video provider contract. No SDK or upstream endpoint is connected."""

from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class GenerationRequest:
    model: str
    kind: Literal["image", "video"]
    prompt: str


@dataclass(frozen=True)
class GenerationResult:
    asset_ids: tuple[str, ...]


class MediaProvider(Protocol):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Reserved adapter boundary; no generation implementation."""
        ...
