from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

class Provider(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    url: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    apis: List["API"] = Relationship(back_populates="provider")

class DiscoverySource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True) # e.g., "github", "apis.guru"
    source_url: str
    last_scanned: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class API(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    base_url: Optional[str] = None
    openapi_spec_url: Optional[str] = None
    version: Optional[str] = None
    provider_id: Optional[int] = Field(default=None, foreign_key="provider.id")
    source_id: Optional[int] = Field(default=None, foreign_key="discoverysource.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    provider: Optional[Provider] = Relationship(back_populates="apis")
    endpoints: List["Endpoint"] = Relationship(back_populates="api")

class Endpoint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    api_id: int = Field(foreign_key="api.id")
    path: str = Field(index=True)
    method: str = Field(index=True) # GET, POST, etc.
    description: Optional[str] = None
    parameters: Optional[str] = None # JSON string of parameters
    responses: Optional[str] = None # JSON string of responses
    created_at: datetime = Field(default_factory=datetime.utcnow)

    api: API = Relationship(back_populates="endpoints")
