from sqladmin import ModelView
from sqladmin.filters import StaticValuesFilter

from src.models.tasks import Task


class TaskAdmin(ModelView, model=Task):
    column_list = [
        Task.id,
        Task.deadline,
        Task.status,
        Task.executor,
        Task.author,
        Task.description,
        Task.created_at,
    ]
    form_include_pk = True
    form_excluded_columns = [
        Task.team_id,
        Task.author_id,
        Task.executor_id,
        Task.created_at,
        Task.updated_at,
        Task.id,
    ]
    column_searchable_list = [Task.description]
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
