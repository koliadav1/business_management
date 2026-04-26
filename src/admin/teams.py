from sqladmin import ModelView

from src.models.teams import Team


class TeamAdmin(ModelView, model=Team):
    column_list = [
        Team.id,
        Team.name,
        Team.description,
        Team.invite_code,
        Team.created_at,
    ]
    form_excluded_columns = [
        Team.created_at,
        Team.updated_at,
        Team.id,
        Team.team_tasks,
        Team.invite_code,
    ]
    column_searchable_list = [Team.name, Team.description, Team.invite_code]
