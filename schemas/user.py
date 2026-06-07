from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class VerifyResponse(BaseModel):
    valid: bool
    user: Optional[UserPublic] = None
    message: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "user"

    @field_validator("role")
    @classmethod
    def role_valid(cls, v):
        if v not in ("admin", "user"):
            raise ValueError("role debe ser 'admin' o 'user'")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("La contrasena debe tener al menos 6 caracteres")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("role")
    @classmethod
    def role_valid(cls, v):
        if v is not None and v not in ("admin", "user"):
            raise ValueError("role debe ser 'admin' o 'user'")
        return v


class UserListResponse(BaseModel):
    total: int
    users: list[UserPublic]
