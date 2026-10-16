import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(default=False)


class PlayerEvent(Base):
    __tablename__ = "player_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True)  # evita duplicatas
    session_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    game_time_seconds: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(20))
    event_type: Mapped[str] = mapped_column(String(50))
    object_name: Mapped[str | None] = mapped_column(String(100))