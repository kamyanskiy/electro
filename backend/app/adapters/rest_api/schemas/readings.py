"""Reading schemas."""

from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class ReadingCreateRequest(BaseModel):
    """Reading creation request schema."""

    day_reading: Decimal = Field(..., ge=0, le=99999.99, decimal_places=2, description="Day reading in kWh")
    night_reading: Decimal = Field(..., ge=0, le=99999.99, decimal_places=2, description="Night reading in kWh")

    @field_validator('day_reading', 'night_reading')
    @classmethod
    def validate_decimal_places(cls, v):
        """Ensure readings have at most 2 decimal places."""
        if v is not None:
            # Convert to string and check decimal places
            str_value = str(v)
            if '.' in str_value:
                integer_part, decimal_part = str_value.split('.')
                if len(decimal_part) > 2:
                    raise ValueError('Must have at most 2 decimal places')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "day_reading": 123.45,
                    "night_reading": 67.89
                }
            ]
        }
    }


class ReadingResponse(BaseModel):
    """Reading response schema."""

    id: int
    user_id: UUID
    day_reading: Decimal
    night_reading: Decimal
    reading_date: date
    is_update: bool = False

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "day_reading": 123.45,
                    "night_reading": 67.89,
                    "reading_date": "2026-01-23",
                    "is_update": False
                }
            ]
        }
    }


class ReadingListResponse(BaseModel):
    """List of readings response schema."""

    readings: list[ReadingResponse]
    total: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "readings": [
                        {
                            "id": 1,
                            "user_id": "550e8400-e29b-41d4-a716-446655440000",
                            "day_reading": 123.45,
                            "night_reading": 67.89,
                            "reading_date": "2026-01-23",
                            "is_update": False
                        }
                    ],
                    "total": 1
                }
            ]
        }
    }


class ReadingCheckResponse(BaseModel):
    """Response for checking if reading exists for today."""

    exists: bool
    reading: ReadingResponse | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "exists": True,
                    "reading": {
                        "id": 1,
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "day_reading": 123.45,
                        "night_reading": 67.89,
                        "reading_date": "2026-01-23",
                        "is_update": False
                    }
                }
            ]
        }
    }


class ReadingWithUserResponse(BaseModel):
    """Reading with user info response schema (for admin)."""

    id: int
    user_id: UUID
    plot_number: str
    username: str
    day_reading: Decimal
    night_reading: Decimal
    reading_date: date

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "plot_number": "123",
                    "username": "ivan",
                    "day_reading": 123.45,
                    "night_reading": 67.89,
                    "reading_date": "2026-01-23"
                }
            ]
        }
    }


class AdminReadingsListResponse(BaseModel):
    """List of readings with user info response schema (for admin)."""

    readings: list[ReadingWithUserResponse]
    total: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "readings": [
                        {
                            "id": 1,
                            "user_id": "550e8400-e29b-41d4-a716-446655440000",
                            "plot_number": "123",
                            "username": "ivan",
                            "day_reading": 123.45,
                            "night_reading": 67.89,
                            "reading_date": "2026-01-23"
                        }
                    ],
                    "total": 1
                }
            ]
        }
    }
