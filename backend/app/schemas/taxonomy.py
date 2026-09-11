from typing import Optional
from pydantic import BaseModel, ConfigDict

class CategorySchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class RegionSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CountrySchema(BaseModel):
    id: str
    name: str
    model_config = ConfigDict(from_attributes=True)

class CuisineSchema(BaseModel):
    id: str
    name: str
    region_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class DietTypeSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class NutrientSchema(BaseModel):
    id: str
    name: str
    unit: str
    category: str
    model_config = ConfigDict(from_attributes=True)

class SourceSchema(BaseModel):
    id: str
    name: str
    version: Optional[str] = None
    organization: Optional[str] = None
    country: Optional[str] = None
    url: Optional[str] = None
    basis: Optional[str] = None
    license_status: Optional[str] = None
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
