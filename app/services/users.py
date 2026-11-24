"""User preference service."""
from app.db.repositories import upsert_user, set_notifications, set_favorite_team, get_user


def register_user(user):
    return upsert_user(user.id, user.id, user.username)


def enable_notifications(user_id: int, enabled: bool):
    set_notifications(user_id, enabled)


def choose_team(user_id: int, team: str | None):
    set_favorite_team(user_id, team)
