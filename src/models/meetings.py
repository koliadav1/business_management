from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    DateTime,
    func,
    UniqueConstraint,
    Boolean,
)
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, List

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.users import User
    from src.models.teams import Team


class MeetingMember(Base):
    __tablename__ = "meeting_members"
    __table_args__ = (
        UniqueConstraint("member_id", "meeting_id", name="uq_meeting_member"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(1024))
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        CheckConstraint(
            "start_time > CURRENT_TIMESTAMP", name="check_start_time_not_past"
        ),
    )
    duration_m: Mapped[int] = mapped_column(
        Integer, CheckConstraint("duration_m > 0", name="duration_positive")
    )
    initiator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    initiator: Mapped["User"] = relationship(
        back_populates="initiated_meetings", foreign_keys=[initiator_id]
    )
    team: Mapped["Team"] = relationship(
        back_populates="meetings", foreign_keys=[team_id]
    )
    members: Mapped[List["User"]] = relationship(
        back_populates="meetings",
        secondary="meeting_members",
        primaryjoin="Meeting.id == MeetingMember.meeting_id",
        secondaryjoin="User.id == MeetingMember.member_id",
    )

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes=self.duration_m)

    @property
    def is_finished(self):
        return self.is_active and datetime.now(timezone.utc) > self.end_time

    def __str__(self):
        return f"Meeting at {self.start_time}"
