from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter

from src.api.schemas.api.v1.users import (
    RequestUserCreate,
    ResponseUser,
)
from src.api.services.user import UserService, get_user_service
from src.api.validators.user import (
    UserValidator,
    get_user_validator,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=ResponseUser,
    summary="Register the user",
    dependencies=[Depends(RateLimiter(times=5, seconds=1))],
)
async def register_user(
    body: RequestUserCreate,
    user_service: UserService = Depends(get_user_service),
    user_validator: UserValidator = Depends(get_user_validator),
) -> ResponseUser:
    """Register the user

    Returns:
    - **ResponseUser**: User details
    """
    await user_validator.is_duplicate_email(body.email)
    await user_validator.is_duplicate_username(body.username)
    user = await user_service.create(body)
    return user


@router.post(
    "/token",
    response_model=dict[str, str],
    summary="Login user by issuing a JWT token",
    dependencies=[Depends(RateLimiter(times=5, seconds=1))],
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> dict[str, str]:
    """Endpoint to receive JWT

    Issuing a JWT token

    Returns:
    - **StringRepresent**: Status code with message "The login was completed successfully"
    """
    token = await user_service.login(form_data)
    return token
