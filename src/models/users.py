from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func
from sqlalchemy import Enum as SQLEnum
from fastapi_users.db import SQLAlchemyBaseUserTable
from datetime import datetime
from enum import Enum
from typing import List, TYPE_CHECKING

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.tasks import Tasks


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class Users(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.USER, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), server_onupdate=func.now()
    )

    assigned_tasks: Mapped[List["Tasks"]] = relationship(
        back_populates="executor", foreign_keys="Tasks.executor_id"
    )
    created_tasks: Mapped[List["Tasks"]] = relationship(
        back_populates="author", foreign_keys="Tasks.author_id"
    )
