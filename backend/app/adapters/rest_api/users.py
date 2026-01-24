"""User-related API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.core.models.user import User
from app.core.services.registration import RegistrationService
from app.core.services.authentication import AuthenticationService
from app.adapters.rest_api.schemas.users import (
    UserRegisterRequest,
    UserResponse,
    ActivationStatusResponse
)
from app.adapters.rest_api.schemas.auth import LoginRequest, TokenResponse
from app.adapters.rest_api.dependencies import get_current_user
from app.container import Container

router = APIRouter()


@router.post(
    "/users/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user with plot number, username, email, and password. User will be inactive until activated by admin."
)
async def register_user(
    user_data: UserRegisterRequest,
    registration_service: RegistrationService = Depends(lambda: Container.registration_service())
):
    """Register a new user."""
    try:
        user = await registration_service.register_user(
            plot_number=user_data.plot_number,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        return UserResponse(
            id=user.id,
            plot_number=user.plot_number,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            activated_at=user.activated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/users/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user with username and password, returns JWT access token and user information."
)
async def login_user(
    username: str = Form(...),
    password: str = Form(...),
    auth_service: AuthenticationService = Depends(lambda: Container.authentication_service())
):
    """Authenticate user and return access token and user information."""
    try:
        token, user = await auth_service.authenticate(
            username=username,
            password=password
        )
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                plot_number=user.plot_number,
                username=user.username,
                email=user.email,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at,
                activated_at=user.activated_at
            )
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get(
    "/users/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information."
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        plot_number=current_user.plot_number,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        activated_at=current_user.activated_at
    )


@router.get(
    "/users/me/activation-status",
    response_model=ActivationStatusResponse,
    summary="Check activation status",
    description="Check if current user is activated."
)
async def check_activation_status(current_user: User = Depends(get_current_user)):
    """Check user activation status."""
    return ActivationStatusResponse(
        is_active=current_user.is_active,
        role=current_user.role.value,
        activated_at=current_user.activated_at
    )