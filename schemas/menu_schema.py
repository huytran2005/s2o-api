from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Dict, Any
from decimal import Decimal

class MenuCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category_id: UUID
    image_url: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
class MenuOut(BaseModel):
    id: UUID
    name: str
    price: Decimal
    image_url: Optional[str] = None
    is_available: bool

    class Config:
        from_attributes = True
