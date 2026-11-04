"""Tool discovery/execution contracts; no tool or MCP server is registered."""

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
        """Execution, approval and receipts are not implemented."""
        ...
