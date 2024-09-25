from pydantic import BaseModel, EmailStr, Field

from src.api.schemas.api.v1.base import (
    LoginMixin,
    TimeMixin,
    UUIDMixin,
)


class User(BaseModel):
    username: str = Field(
        description="Юзернейм пользователя",
        examples=["Badass"],
        min_length=1,
        max_length=64,
    )


class RequestUserCreate(User, LoginMixin):
    pass


class ResponseUser(User, UUIDMixin, TimeMixin):
    email: EmailStr = Field(
        description="Email пользователя",
        examples=["exemple@mail.ru"],
        min_length=1,
        max_length=64,
    )
    is_superuser: bool = Field(
        description="Флаг - является ли пользователь администратором",
        examples=[False],
    )

    class Meta:
        abstract = True
