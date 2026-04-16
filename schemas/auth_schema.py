from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# =========================
# BASE USER
# =========================
class BaseUserSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    display_name: Optional[str] = None
    phone: Optional[str] = None


# =========================
# REGISTER CUSTOMER
# =========================
class RegisterRequest(BaseUserSchema):
    pass


class RegisterResponse(BaseModel):
    message: str


# =========================
# REGISTER OWNER
# =========================
class RegisterOwnerRequest(BaseUserSchema):
    pass   # 🔥 đã bỏ restaurant_name


# =========================
# LOGIN
# =========================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"