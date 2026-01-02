from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel

class OrderItemCreate(BaseModel):
    menu_item_id: UUID
    qty: int
    note: Optional[str] = None

class OrderCreate(BaseModel):
    session_token: str
    items: List[OrderItemCreate]

class OrderLineResponse(BaseModel):
    id: UUID
    item_name: str
    qty: int
    unit_price: float
    note: Optional[str]

class OrderResponse(BaseModel):
    id: UUID
    status: str
    total_amount: float
    lines: List[OrderLineResponse]
