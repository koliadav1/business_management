from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.users import User


class CommentService:
    async def add_comment(
        self, task_id: int, content: str, current_user: User, uow: IUnitOfWork
    ):
        pass
