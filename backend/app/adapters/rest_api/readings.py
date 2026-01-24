"""Readings-related API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.models.user import User
from app.core.services.reading_service import ReadingService
from app.adapters.rest_api.schemas.readings import (
    ReadingCreateRequest,
    ReadingResponse,
    ReadingListResponse,
    ReadingCheckResponse
)
from app.adapters.rest_api.dependencies import get_current_active_user
from app.container import Container

router = APIRouter()


@router.post(
    "/readings",
    response_model=ReadingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit meter reading",
    description="Submit electricity meter readings (day and night). User must be active. If reading for today already exists, it will be updated."
)
async def create_reading(
    reading_data: ReadingCreateRequest,
    current_user: User = Depends(get_current_active_user),
    reading_service: ReadingService = Depends(lambda: Container.reading_service())
):
    """Submit a new meter reading or update existing one for today."""
    try:
        reading, is_update = await reading_service.create_reading(
            day_reading=float(reading_data.day_reading),
            night_reading=float(reading_data.night_reading),
            user=current_user
        )
        return ReadingResponse(
            id=reading.id,
            user_id=reading.user_id,
            day_reading=reading.day_reading,
            night_reading=reading.night_reading,
            reading_date=reading.reading_date,
            is_update=is_update
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/readings/check-today",
    response_model=ReadingCheckResponse,
    summary="Check if reading exists for today",
    description="Check if current user has already submitted a reading for today."
)
async def check_reading_today(
    current_user: User = Depends(get_current_active_user),
    reading_service: ReadingService = Depends(lambda: Container.reading_service())
):
    """Check if user has already submitted reading for today."""
    existing_reading = await reading_service.check_reading_exists_for_today(current_user.id)

    if existing_reading:
        return ReadingCheckResponse(
            exists=True,
            reading=ReadingResponse(
                id=existing_reading.id,
                user_id=existing_reading.user_id,
                day_reading=existing_reading.day_reading,
                night_reading=existing_reading.night_reading,
                reading_date=existing_reading.reading_date,
                is_update=False
            )
        )
    else:
        return ReadingCheckResponse(exists=False, reading=None)


@router.get(
    "/readings",
    response_model=ReadingListResponse,
    summary="Get readings history",
    description="Get meter readings history for current user."
)
async def get_readings(
    limit: int = Query(default=10, ge=1, le=100, description="Number of readings to return"),
    current_user: User = Depends(get_current_active_user),
    reading_service: ReadingService = Depends(lambda: Container.reading_service())
):
    """Get readings history for current user."""
    readings = await reading_service.get_readings_by_user(current_user.id, limit)

    reading_responses = [
        ReadingResponse(
            id=reading.id,
            user_id=reading.user_id,
            day_reading=reading.day_reading,
            night_reading=reading.night_reading,
            reading_date=reading.reading_date,
            is_update=False
        )
        for reading in readings
    ]

    return ReadingListResponse(
        readings=reading_responses,
        total=len(reading_responses)
    )