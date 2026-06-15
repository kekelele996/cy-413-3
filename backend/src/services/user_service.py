from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.constants.error_codes import ERROR_CODES
from src.constants.log_templates import LOG_TEMPLATES
from src.constants.roles import ROLE_MEMBER
from src.middlewares.error_handler import AppError
from src.models.assessment import UserAssessment
from src.models.journal import Journal
from src.models.mood import Mood
from src.models.user import User
from src.schemas.user import ProfileReport, UserCreate, UserUpdate
from src.utils.logger import app_logger
from src.utils.password import hash_password, verify_password


def create_user(db: Session, payload: UserCreate) -> User:
    app_logger.info(LOG_TEMPLATES["USER_REGISTER"].format(email=payload.email, role=ROLE_MEMBER))
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise AppError("USER_EMAIL_EXISTS", ERROR_CODES["USER_EMAIL_EXISTS"], 409)
    user = User(
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        nickname=payload.nickname,
        avatar=payload.avatar,
        birth_date=payload.birth_date,
        gender=payload.gender,
        role=ROLE_MEMBER,
        meditation_days_per_week=payload.meditation_days_per_week,
        meditation_reminder_time=payload.meditation_reminder_time,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    app_logger.info(LOG_TEMPLATES["USER_LOGIN"].format(email=email))
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        raise AppError("AUTH_INVALID_CREDENTIALS", ERROR_CODES["AUTH_INVALID_CREDENTIALS"], 401)
    return user


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    app_logger.info(LOG_TEMPLATES["USER_PROFILE_UPDATE"].format(user_id=user.id, nickname=payload.nickname or user.nickname))
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def get_week_range(today: date | None = None) -> tuple[date, date]:
    today = today or date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_meditation_week_stats(db: Session, user: User) -> tuple[int, int, float]:
    start, end = get_week_range()
    completed = db.scalar(
        select(func.count(Journal.id))
        .where(Journal.user_id == user.id)
        .where(Journal.is_meditation == True)
        .where(func.date(Journal.created_at) >= start)
        .where(func.date(Journal.created_at) <= end)
    )
    completed = int(completed or 0)
    target = user.meditation_days_per_week
    rate = round(completed / target * 100, 2) if target > 0 else 0.0
    return completed, target, rate


def profile_report(db: Session, user: User) -> ProfileReport:
    app_logger.info(LOG_TEMPLATES["USER_PROFILE_READ"].format(user_id=user.id))
    avg_mood = db.scalar(select(func.coalesce(func.avg(Mood.mood_level), 0)).where(Mood.user_id == user.id))
    mood_count = db.scalar(select(func.count(Mood.id)).where(Mood.user_id == user.id))
    assessment_count = db.scalar(select(func.count(UserAssessment.id)).where(UserAssessment.user_id == user.id))
    journal_count = db.scalar(select(func.count(Journal.id)).where(Journal.user_id == user.id))
    meditation_completed, meditation_target, meditation_rate = get_meditation_week_stats(db, user)
    return ProfileReport(
        user=user,
        avg_mood=round(float(avg_mood or 0), 2),
        mood_count=int(mood_count or 0),
        assessment_count=int(assessment_count or 0),
        journal_count=int(journal_count or 0),
        meditation_week_completion_rate=meditation_rate,
        meditation_week_completed=meditation_completed,
        meditation_week_target=meditation_target,
    )
