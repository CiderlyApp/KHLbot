"""Small synchronous repository; operations are short and local to each update."""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .base import get_session_factory
from .models import User, SentNotification


def upsert_user(telegram_id: int, chat_id: int, username: str | None = None) -> User:
    with get_session_factory()() as db:
        user = db.get(User, telegram_id)
        if user is None:
            user = User(telegram_id=telegram_id, chat_id=chat_id, username=username)
            db.add(user)
        else:
            user.chat_id = chat_id
            user.username = username
        db.commit()
        db.refresh(user)
        return user


def get_user(telegram_id: int) -> User | None:
    with get_session_factory()() as db:
        return db.get(User, telegram_id)


def set_notifications(telegram_id: int, enabled: bool) -> None:
    with get_session_factory()() as db:
        user = db.get(User, telegram_id)
        if user:
            user.notifications_enabled = enabled
            db.commit()


def set_favorite_team(telegram_id: int, team: str | None) -> None:
    with get_session_factory()() as db:
        user = db.get(User, telegram_id)
        if user:
            user.favorite_team = team
            db.commit()


def get_subscribers():
    with get_session_factory()() as db:
        return list(db.scalars(select(User).where(User.notifications_enabled.is_(True))).all())


def was_notification_sent(telegram_id: int, match_id: str) -> bool:
    with get_session_factory()() as db:
        stmt = select(SentNotification.id).where(
            SentNotification.telegram_id == telegram_id,
            SentNotification.match_id == match_id,
        )
        return db.scalar(stmt) is not None


def mark_notification_sent(telegram_id: int, match_id: str) -> None:
    with get_session_factory()() as db:
        db.add(SentNotification(telegram_id=telegram_id, match_id=match_id))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
