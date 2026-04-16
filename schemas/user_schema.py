from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# =========================
# CREATE STAFF REQUEST
# =========================
class CreateStaffRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    display_name: Optional[str] = None
    phone: Optional[str] = None


# =========================
# CREATE STAFF RESPONSE
# =========================
class CreateStaffResponse(BaseModel):
    message: str
    staff_id: str
    restaurant_id: str