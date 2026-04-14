from sqladmin import ModelView
from sqladmin.filters import StaticValuesFilter
from sqlalchemy import or_
from sqlalchemy.orm import aliased

from src.models.users import User
from src.models.tasks import Task


class TaskAdmin(ModelView, model=Task):
    column_list = [
        Task.id,
        Task.description,
        Task.status,
        Task.executor,
        Task.author,
        Task.deadline,
        Task.created_at,
    ]
    form_excluded_columns = [
        Task.team_id,
        Task.author_id,
        Task.executor_id,
        Task.created_at,
        Task.updated_at,
        Task.id,
    ]
    column_searchable_list = [Task.description, "Executor", "Author"]
    column_filters = [
        StaticValuesFilter(
            Task.status,
            [
                ("NEW", "New"),
                ("IN_PROGRESS", "In progress"),
                ("DONE", "Done"),
                ("CANCELLED", "Cancelled"),
            ],
            title="Status",
        ),
    ]

    def search_query(self, stmt, term):
        search_term = f"%{term}%"
        u1 = aliased(User)
        u2 = aliased(User)

        return (
            stmt.outerjoin(u1, Task.author)
            .outerjoin(u2, Task.executor)
            .filter(
                or_(
                    Task.description.ilike(search_term),
                    u1.email.ilike(search_term),
                    u2.email.ilike(search_term),
                )
            )
        )
