from sqladmin import ModelView
from sqladmin.filters import ForeignKeyFilter

from src.models.users import User
from src.models.evaluations import Evaluation


class EvaluationAdmin(ModelView, model=Evaluation):
    column_list = [
        Evaluation.id,
        Evaluation.task,
        Evaluation.rating,
        Evaluation.comment,
        Evaluation.rater,
        Evaluation.created_at,
    ]
    form_excluded_columns = [
        Evaluation.rater_id,
        Evaluation.created_at,
        Evaluation.updated_at,
        Evaluation.id,
        Evaluation.task_id,
    ]
    column_searchable_list = [Evaluation.id, "rater.email"]
    column_filters = [
        ForeignKeyFilter(Evaluation.rater_id, User.email, title="Rater"),
    ]
