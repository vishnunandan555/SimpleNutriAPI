from typing import Generic, TypeVar, List, Dict, Any
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    dataset_version: str
    database: str
    environment: str

class VersionResponse(BaseModel):
    service: str
    api_version: str
    dataset_version: str
    schema_version: str
    created_at: str
    source_versions: Dict[str, str]
    counts: Dict[str, int]
    offline_bundle_available: bool
    license_notice: str
