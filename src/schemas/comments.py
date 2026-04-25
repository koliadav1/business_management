from pydantic import BaseModel, ConfigDict, Field

from .dependencies import UtcDateTime


class BaseComment(BaseModel):
    content: str = Field(
        ..., min_length=1, max_length=1024, description="Текст комментария"
    )


class CommentCreate(BaseComment):
    pass


class CommentUpdate(BaseComment):
    pass


class CommentRead(BaseModel):
    id: int
    content: str
    task_id: int
    author_id: int
    created_at: UtcDateTime
    updated_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)
