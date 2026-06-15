from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.constants.error_codes import ERROR_CODES
from src.constants.log_templates import LOG_TEMPLATES
from src.middlewares.error_handler import AppError
from src.models.journal import Journal
from src.models.user import User
from src.schemas.journal import JournalCreate, JournalUpdate
from src.utils.logger import app_logger


def list_journals(db: Session, user: User, mood_level: int | None = None) -> list[Journal]:
    app_logger.info(LOG_TEMPLATES["JOURNAL_LIST"].format(user_id=user.id, mood_level=mood_level or "all"))
    query = select(Journal).where(Journal.user_id == user.id).order_by(Journal.created_at.desc())
    if mood_level:
        query = query.where(Journal.mood_level == mood_level)
    return list(db.scalars(query).all())


def create_journal(db: Session, user: User, payload: JournalCreate) -> Journal:
    app_logger.info(
        LOG_TEMPLATES["JOURNAL_CREATE"].format(
            user_id=user.id, title=payload.title, mood_level=payload.mood_level
        )
    )
    journal = Journal(user_id=user.id, **payload.model_dump())
    db.add(journal)
    db.commit()
    db.refresh(journal)
    return journal


def update_journal(db: Session, user: User, journal_id: int, payload: JournalUpdate) -> Journal:
    journal = db.get(Journal, journal_id)
    if not journal or journal.user_id != user.id:
        raise AppError("JOURNAL_NOT_FOUND", f"Journal[id={journal_id}] update failed: {ERROR_CODES['JOURNAL_NOT_FOUND']}", 404)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(journal, field, value)
    app_logger.info(
        LOG_TEMPLATES["JOURNAL_UPDATE"].format(
            journal_id=journal_id, title=journal.title, is_private=journal.is_private
        )
    )
    db.commit()
    db.refresh(journal)
    return journal


def delete_journal(db: Session, user: User, journal_id: int) -> None:
    journal = db.get(Journal, journal_id)
    if not journal or journal.user_id != user.id:
        raise AppError("JOURNAL_NOT_FOUND", f"Journal[id={journal_id}] delete failed: {ERROR_CODES['JOURNAL_NOT_FOUND']}", 404)
    app_logger.info(LOG_TEMPLATES["JOURNAL_DELETE"].format(journal_id=journal_id, user_id=user.id))
    db.delete(journal)
    db.commit()


def has_meditation_today(db: Session, user: User, today: date | None = None) -> bool:
    today = today or date.today()
    count = db.scalar(
        select(func.count(Journal.id))
        .where(Journal.user_id == user.id)
        .where(Journal.is_meditation == True)
        .where(func.date(Journal.created_at) == today)
    )
    return int(count or 0) > 0


def complete_meditation(db: Session, user: User, note: str | None = None) -> Journal:
    today = date.today()
    if has_meditation_today(db, user, today):
        raise AppError("MEDITATION_ALREADY_COMPLETED", "今日冥想已完成", 409)
    app_logger.info(LOG_TEMPLATES["JOURNAL_CREATE"].format(user_id=user.id, title="今日冥想", mood_level=7))
    journal = Journal(
        user_id=user.id,
        title="今日冥想",
        content=note or "完成了今日的冥想练习，感觉内心平静。",
        mood_level=7,
        is_private=True,
        is_meditation=True,
    )
    db.add(journal)
    db.commit()
    db.refresh(journal)
    return journal

