from pydantic import SecretStr
from sqlalchemy import Boolean, String, false
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from src.db.entities import Entity


class User(Entity):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(64), unique=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, server_default=false())

    def __init__(
        self,
        email: str,
        password: SecretStr,
        username: str,
        is_superuser: bool = False,
    ) -> None:
        self.email = email
        self.password = generate_password_hash(password.get_secret_value())
        self.username = username
        self.is_superuser = is_superuser

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
