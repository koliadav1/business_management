from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.users import User
    from src.models.teams import Team
    from src.models.evaluations import Evaluation


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
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
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
    team: Mapped["Team"] = relationship(
        back_populates="team_tasks", foreign_keys=[team_id]
    )
    evaluation: Mapped["Evaluation"] = relationship(
        back_populates="task", foreign_keys="Evaluation.task_id"
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="task",
        foreign_keys="Comment.task_id",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return self.description


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(1024), nullable=False)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    task: Mapped["Task"] = relationship(
        back_populates="comments", foreign_keys=[task_id]
    )
    author: Mapped["User"] = relationship(
        back_populates="comments", foreign_keys=[author_id]
    )

    def __str__(self):
        return self.content
