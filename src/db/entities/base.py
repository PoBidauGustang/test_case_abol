import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
)

uuid_pk = Annotated[
    str,
    mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    ),
]
created_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=False
    ),
]
updated_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        onupdate=text("NOW()"),
    ),
]


class BaseEntity:
    """Class for base model with standard fields for all models."""

    uuid: Mapped[uuid_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    def __pepr__(self):
        return f"{self.__class__.__name__}(uuid={self.uuid})"


Entity = declarative_base(cls=BaseEntity)
