"""Media adapter contracts and a local SVG renderer."""

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
        """Async media provider extension contract."""
        ...


class LocalImageProvider:
    """Render a fixed-layout card from escaped text, without an AI model."""

    def render(self, model: str, prompt: str) -> bytes:
        from html import escape

        if model not in {"local-poster", "local-badge"}:
            raise ValueError("未知模型")
        color = "#1e4e70" if model == "local-poster" else "#65449a"
        title = escape(prompt[:24])
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="600" viewBox="0 0 960 600">'
            f'<rect width="960" height="600" fill="{color}"/>'
            '<circle cx="790" cy="110" r="210" fill="white" opacity=".08"/>'
            '<text x="70" y="110" fill="#b8d9e8" font-size="24" font-family="sans-serif">AI STUDIO</text>'
            f'<text x="70" y="310" fill="white" font-size="32" font-family="sans-serif">{title}</text>'
            f'<text x="70" y="525" fill="#c6d9ed" font-size="20" font-family="sans-serif">Local SVG renderer / {model}</text>'
            '</svg>'
        ).encode("utf-8")
