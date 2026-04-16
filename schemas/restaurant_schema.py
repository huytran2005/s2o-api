from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ======================
# STAFF RESPONSE
# ======================
class StaffResponse(BaseModel):
    id: UUID
    email: str
    display_name: Optional[str] = None
    phone: Optional[str] = None
    role: str


# ======================
# RESTAURANT
# ======================
class RestaurantBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_preview: Optional[str] = None


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_preview: Optional[str] = None


class RestaurantResponse(RestaurantBase):
    id: UUID
    staff_members: List[StaffResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
