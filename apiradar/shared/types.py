"""
Shared type definitions used by both the backend and TUI.
Keeps the data contract in one place.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class APIRecord:
    id: Optional[int]
    name: str
    description: Optional[str]
    base_url: Optional[str]
    openapi_spec_url: Optional[str]
    version: Optional[str]
    provider_id: Optional[int]
    created_at: Optional[datetime] = None
    endpoints: List["EndpointRecord"] = field(default_factory=list)


@dataclass
class EndpointRecord:
    id: Optional[int]
    api_id: int
    path: str
    method: str
    description: Optional[str] = None


@dataclass
class ProviderRecord:
    id: Optional[int]
    name: str
    url: Optional[str] = None
    description: Optional[str] = None


@dataclass
class DiscoverySourceRecord:
    id: Optional[int]
    name: str
    source_url: str
    last_scanned: Optional[datetime] = None
