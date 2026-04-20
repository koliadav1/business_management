from sqladmin import ModelView
from sqladmin.filters import BooleanFilter

from src.models.meetings import Meeting


class MeetingAdmin(ModelView, model=Meeting):
    column_list = [
        Meeting.id,
        Meeting.description,
        Meeting.duration_m,
        Meeting.start_time,
        Meeting.team,
        Meeting.initiator,
        "is_finished",
        Meeting.is_active,
    ]
    form_columns = [
        Meeting.description,
        Meeting.start_time,
        Meeting.duration_m,
        Meeting.initiator,
        Meeting.is_active,
        Meeting.team,
        Meeting.members,
    ]
    column_searchable_list = [
        Meeting.id,
        "team.name",
        "members.email",
        Meeting.description,
    ]
    column_filters = [
        BooleanFilter(Meeting.is_active),
        BooleanFilter("is_finished"),
    ]
