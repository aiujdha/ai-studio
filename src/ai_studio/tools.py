"""Tool discovery contracts and local text tools."""

from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    effect: Literal["read_only", "generation", "workspace_write"]


class ToolRegistry(Protocol):
    def list_tools(self) -> tuple[ToolSpec, ...]:
        ...

    async def execute(
        self, run_id: str, tool_name: str, arguments: dict[str, object]
    ) -> dict[str, object]:
        """Async extension contract; LocalTools provides synchronous local tools."""
        ...


class LocalTools:
    def list_tools(self) -> tuple[ToolSpec, ...]:
        return (
            ToolSpec("text.inspect", "统计字符数和行数", "read_only"),
            ToolSpec("text.uppercase", "将英文字母转为大写", "read_only"),
        )

    def execute(self, name: str, text: str) -> dict:
        if name == "text.inspect":
            return {"characters": len(text), "lines": len(text.splitlines()), "preview": text[:100]}
        if name == "text.uppercase":
            return {"text": text.upper()}
        raise ValueError("未知工具")
