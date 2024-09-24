from datetime import UTC, datetime, timedelta
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from src.api.schemas.api.v1.users import (
    RequestUserCreate,
    ResponseUser,
)
from src.api.schemas.db.user import UserDB
from src.db.repositories.user import UserRepository, get_user_repository

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/users/token")


class UserService:
    def __init__(self, user_repository: UserRepository, model: BaseModel):
        self._repository = user_repository
        self._model = model

    async def _create_access_token(
        self,
        data: dict[str, str | datetime],
        expires_delta: timedelta | None = None,
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def create(self, obj: RequestUserCreate) -> ResponseUser:
        obj = await self._repository.create(obj)
        model = self._model.model_validate(obj, from_attributes=True)
        return model

    async def login(
        self,
        form_data: OAuth2PasswordRequestForm,
    ) -> dict[str, str]:
        user: BaseModel | None = await self._repository.get_by_username(
            form_data.username
        )
        if not user:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="The email is not valid",
            )
        if not user.check_password(form_data.password):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Bad username or password",
            )
        access_token = await self._create_access_token(
            {"sub": user.username, "is_admin": user.is_superuser}
        )

        return {"access_token": access_token, "token_type": "bearer"}


async def get_me(
    token: str = Depends(oauth2_scheme),
    repository: UserRepository = Depends(get_user_repository),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception from None
    except JWTError:
        raise credentials_exception from None
    user: BaseModel | None = await repository.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user


async def is_admin(current_user=Depends(get_me)):
    if not current_user.is_superuser:
        credentials_exception = HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not allowed, only for administrator",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise credentials_exception


@lru_cache
def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository, UserDB)
