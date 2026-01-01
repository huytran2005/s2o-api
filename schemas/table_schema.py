from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class TableCreate(BaseModel):
    restaurant_id: UUID
    name: str
    seats: int


class TableUpdate(BaseModel):
    name: Optional[str] = None
    seats: Optional[int] = None
    status: Optional[str] = None


class TableOut(BaseModel):
    id: UUID
    restaurant_id: UUID
    name: str
    seats: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
