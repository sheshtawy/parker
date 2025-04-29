from typing import List, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, field_validator, RootModel
from constants import DEFAULT_VEHICLE_WIDTH


@dataclass
class Listing:
    id: str
    width: int
    length: int
    price_in_cents: int
    location_id: Optional[str] = None
    area: int = field(init=False, repr=False)
    
    def __post_init__(self):
        self.area = self.width * self.length

@dataclass
class Location:
    id: str
    listings: List[Listing] = field(default_factory=list)
    
    @property
    def total_area(self) -> int:
        return sum(listing.area for listing in self.listings) if self.listings else 0

# API models
# ----------
class VehicleEntry(BaseModel):
    length: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

class VehicleEntryList(RootModel[List[VehicleEntry]]):
    """
    Root model that accepts a JSON array of vehicle entries.
    """
    
    @field_validator('root')
    @classmethod
    def validate_total_quantity(cls, v):
        total_quantity = sum(item.quantity for item in v)
        if total_quantity > 5:
            raise ValueError("Total number of vehicles cannot exceed 5")
        return v
    
    @field_validator('root')
    @classmethod
    def validate_non_empty(cls, v):
        if not v:
            raise ValueError("At least one vehicle entry is required")
        return v
    
    @property
    def total_area(self):
        total_area = 0
        for entry in self.root:
            total_area += entry.length * entry.quantity * DEFAULT_VEHICLE_WIDTH  # multiply by default width
        return total_area

class VehicleResponse(BaseModel):
    location_id: str
    listing_ids: List[str]
    total_price_in_cents: int

class SearchResult(BaseModel):
    location_id: str
    listing_ids: List[str]
    total_price_in_cents: int