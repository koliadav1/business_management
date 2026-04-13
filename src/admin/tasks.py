from sqladmin import ModelView

from src.models.tasks import Task


class TaskAdmin(ModelView, model=Task):
    pass
