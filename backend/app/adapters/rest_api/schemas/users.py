"""User schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """User registration request schema."""

    plot_number: str = Field(..., min_length=1, max_length=50, description="Plot number")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "plot_number": "001",
                    "username": "user123",
                    "email": "user@example.com",
                    "password": "password123"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    plot_number: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    activated_at: datetime | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "plot_number": "001",
                    "username": "user123",
                    "email": "user@example.com",
                    "role": "user",
                    "is_active": False,
                    "created_at": "2026-01-23T10:00:00Z",
                    "activated_at": None
                }
            ]
        }
    }


class ActivationStatusResponse(BaseModel):
    """User activation status response."""

    is_active: bool
    role: str
    activated_at: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "is_active": True,
                    "role": "user",
                    "activated_at": "2026-01-23T11:00:00Z"
                }
            ]
        }
    }
