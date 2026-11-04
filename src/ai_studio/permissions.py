"""Administrative role and user tier are independent dimensions."""

from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class UserContext:
    user_id: str
    role: Literal["user", "admin"]
    user_type: Literal["standard", "professional"]


class AccessPolicy(Protocol):
    def require_module_access(self, user: UserContext, module: str) -> None:
        """An implementation must reject unauthorized access; none is supplied."""
        ...
