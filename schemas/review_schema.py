from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    order_line_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewStats(BaseModel):
    avg_rating: float
    total_reviews: int
