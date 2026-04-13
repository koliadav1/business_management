from sqladmin import ModelView

from src.models.tasks import Task


class TaskAdmin(ModelView, model=Task):
    column_list = [
        Task.id,
        Task.deadline,
        Task.status,
        Task.executor,
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
