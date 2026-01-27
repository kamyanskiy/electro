"""Authentication schemas."""

from pydantic import BaseModel, Field
from app.adapters.rest_api.schemas.users import UserResponse


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str = Field(..., min_length=3, max_length=50, description="Username or email")
    password: str = Field(..., min_length=6, description="Password")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "user123",
                    "password": "password123"
                },
                {
                    "username": "user@example.com",
                    "password": "password123"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "plot_number": "001",
                        "username": "user123",
                        "email": "user@example.com",
                        "role": "user",
                        "is_active": False,
                        "created_at": "2026-01-23T10:00:00Z",
                        "activated_at": None
                    }
                }
            ]
        }
    }
