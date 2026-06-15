from sqlalchemy.orm import Session

from src.models.journal import Journal
from src.models.user import User
from src.schemas.journal import JournalCreate, JournalUpdate
from src.services import journal_service
from src.utils.logger import app_logger


def list_journals(db: Session, current_user: User, mood_level: int | None) -> list[Journal]:
    try:
        return journal_service.list_journals(db, current_user, mood_level)
    except Exception as exc:
        app_logger.error("Journal[user_id=%s] controller list failed: %s", current_user.id, exc)
        raise


def create_journal(db: Session, current_user: User, payload: JournalCreate) -> Journal:
    try:
        return journal_service.create_journal(db, current_user, payload)
    except Exception as exc:
        app_logger.error("Journal[user_id=%s] controller create failed: %s", current_user.id, exc)
        raise


def update_journal(db: Session, current_user: User, journal_id: int, payload: JournalUpdate) -> Journal:
    try:
        return journal_service.update_journal(db, current_user, journal_id, payload)
    except Exception as exc:
        app_logger.error("Journal[id=%s] controller update failed: %s", journal_id, exc)
        raise


def delete_journal(db: Session, current_user: User, journal_id: int) -> dict[str, str]:
    try:
        journal_service.delete_journal(db, current_user, journal_id)
        return {"message": f"Journal[id={journal_id}] delete success"}
    except Exception as exc:
        app_logger.error("Journal[id=%s] controller delete failed: %s", journal_id, exc)
        raise


def has_meditation_today(db: Session, current_user: User) -> dict[str, bool]:
    try:
        return {"completed": journal_service.has_meditation_today(db, current_user)}
    except Exception as exc:
        app_logger.error("Meditation[user_id=%s] controller check failed: %s", current_user.id, exc)
        raise


def complete_meditation(db: Session, current_user: User, note: str | None = None) -> Journal:
    try:
        return journal_service.complete_meditation(db, current_user, note)
    except Exception as exc:
        app_logger.error("Meditation[user_id=%s] controller complete failed: %s", current_user.id, exc)
        raise

