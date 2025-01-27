from dataclasses import dataclass
from uuid import UUID

__all__ = [
    "Organization",
    "Hub",
]


@dataclass(frozen=True, kw_only=True)
class Hub:
    """Hub metadata."""

    url: str
    """Hub URL."""

    code: str
    """Hub shortcode."""

    display_name: str
    """Hub display name."""

    services: tuple[str, ...]
    """List of service codes."""


@dataclass(frozen=True, kw_only=True)
class Organization:
    """License holder organization metadata."""

    id: UUID
    """Organization ID."""

    display_name: str
    """Organization display name."""

    hubs: tuple[Hub, ...]
