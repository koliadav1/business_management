from sqladmin import ModelView

from src.models.tasks import Comment


class CommentAdmin(ModelView, model=Comment):
    column_list = [
        Comment.id,
        Comment.content,
        Comment.author,
        Comment.task,
        Comment.created_at,
    ]

    can_create = False
    can_edit = False
    can_delete = True

    column_searchable_list = [
        Comment.content,
        "author.email",
        "task.description",
    ]
