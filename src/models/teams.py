from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func
from datetime import datetime
from typing import TYPE_CHECKING, List

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.users import User
    from src.models.tasks import Task


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str | None] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    members: Mapped[List["User"]] = relationship(
        back_populates="team", foreign_keys="User.team_id"
    )
    team_tasks: Mapped[List["Task"]] = relationship(
        back_populates="team",
        foreign_keys="Task.team_id",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return self.name
