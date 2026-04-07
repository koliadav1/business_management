from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.users import User


class TaskStatus(Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(1024))
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), default=TaskStatus.NEW, nullable=False, index=True
    )
    executor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    executor: Mapped["User"] = relationship(
        back_populates="assigned_tasks", foreign_keys=[executor_id]
    )
    author: Mapped["User"] = relationship(
        back_populates="created_tasks", foreign_keys=[author_id]
    )
