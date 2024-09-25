from pydantic import EmailStr

from src.api.schemas.db.base import BaseMixin


class UserDB(BaseMixin):
    email: EmailStr
    username: str
    is_superuser: bool = False
