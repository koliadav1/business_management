from sqladmin import ModelView

from src.models.teams import Team


class TeamAdmin(ModelView, model=Team):
    pass
