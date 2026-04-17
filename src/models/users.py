from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy import Enum as SQLEnum
from fastapi_users.db import SQLAlchemyBaseUserTable
from datetime import datetime
from enum import Enum
from typing import List, TYPE_CHECKING

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.evaluations import Evaluation
    from src.models.tasks import Task
    from src.models.teams import Team
    from src.models.meetings import Meeting, MeetingMember


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.USER, nullable=False
    )
    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    assigned_tasks: Mapped[List["Task"]] = relationship(
        back_populates="executor", foreign_keys="Task.executor_id"
    )
    created_tasks: Mapped[List["Task"]] = relationship(
        back_populates="author", foreign_keys="Task.author_id"
    )
    team: Mapped["Team"] = relationship(
        back_populates="members", foreign_keys=[team_id]
    )
    evaluations: Mapped[List["Evaluation"]] = relationship(
        back_populates="rater", foreign_keys="Evaluation.rater_id"
    )
    initiated_meetings: Mapped[List["Meeting"]] = relationship(
        back_populates="initiator", foreign_keys="Meeting.initiator_id"
    )
    meetings: Mapped[List["MeetingMember"]] = relationship(
        back_populates="user",
        foreign_keys="MeetingMember.member_id",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return self.email
