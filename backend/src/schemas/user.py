from datetime import date, datetime, time

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    nickname: str = Field(min_length=1, max_length=100)
    avatar: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    meditation_days_per_week: int = Field(default=3, ge=1, le=7)
    meditation_reminder_time: time | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=100)
    avatar: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    meditation_days_per_week: int | None = Field(default=None, ge=1, le=7)
    meditation_reminder_time: time | None = None


class UserRead(UserBase):
    id: int
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class ProfileReport(BaseModel):
    user: UserRead
    avg_mood: float
    mood_count: int
    assessment_count: int
    journal_count: int
    meditation_week_completion_rate: float
    meditation_week_completed: int
    meditation_week_target: int

