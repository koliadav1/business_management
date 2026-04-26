from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Index, String, DateTime, func
from sqlalchemy import Enum as SQLEnum
from fastapi_users.db import SQLAlchemyBaseUserTable
from datetime import datetime
from enum import Enum
from typing import List, TYPE_CHECKING

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.evaluations import Evaluation
    from src.models.tasks import Task, Comment
    from src.models.teams import Team
    from src.models.meetings import Meeting


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
    phone_number: Mapped[str | None] = mapped_column(
        String(20), nullable=True, unique=True
    )
    name: Mapped[str | None] = mapped_column(String(30), nullable=True)
    surname: Mapped[str | None] = mapped_column(String(30), nullable=True)
    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id", ondelete="SET NULL")
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
    meetings: Mapped[List["Meeting"]] = relationship(
        back_populates="members",
        secondary="meeting_members",
        primaryjoin="User.id == MeetingMember.member_id",
        secondaryjoin="Meeting.id == MeetingMember.meeting_id",
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="author", foreign_keys="Comment.author_id"
    )

    __table_args__ = (Index("ix_team_role", "team_id", "role"),)

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        if self.name and self.surname:
            return self.name + " " + self.surname
        elif self.name:
            return self.name
        elif self.surname:
            return self.surname
        else:
            return None
