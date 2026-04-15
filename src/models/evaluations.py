from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    DateTime,
    func,
)
from datetime import datetime
from typing import TYPE_CHECKING

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.tasks import Task
    from src.models.users import User


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        unique=True,
    )
    rating: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("rating >= 1 and rating <= 5", name="rating_range"),
        nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(String(1024))
    rater_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    task: Mapped["Task"] = relationship(
        back_populates="evaluation", foreign_keys=[task_id]
    )
    rater: Mapped["User"] = relationship(
        back_populates="evaluations", foreign_keys=[rater_id]
    )

    def __str__(self):
        return f"Оценка: {self.rating}"
