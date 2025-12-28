from pydantic import BaseModel
from uuid import UUID
from typing import Optional
class CategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = None


class CategoryOut(BaseModel):
    id: UUID
    name: str
    icon: Optional[str] = None

    class Config:
        from_attributes = True
