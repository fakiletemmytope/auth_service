from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, func, Enum as SAEnum
import enum
from datetime import datetime


class Role(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(
        index=True,
        unique=True,
        nullable=False,
    )
    password: str
    role: Role = Field(
        default=Role.USER,
        nullable=False,
    )
    is_active: bool = Field(default=True)
    date_created: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # handled by Postgres
            nullable=False,
        )
    )
    date_updated: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),  # auto update on row change
            nullable=False,
        )
    )