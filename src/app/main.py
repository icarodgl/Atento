from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import PlayerEvent, User
from app.schemas.schema import EventBatch, EventOut, Token
from app.security import (
    create_access_token,
    get_admin,
    get_current_user,
    verify_password,
)

app = FastAPI(title="Jogo Analytics API")

DbDep = Annotated[Session, Depends(get_db)]


@app.post("/auth/token", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbDep):
    user = db.scalar(select(User).where(User.username == form.username))
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.username), token_type="bearer")


@app.post("/events", status_code=201)
def receive_events(
    batch: EventBatch,
    db: DbDep,
    user: Annotated[User, Depends(get_current_user)],
):
    rows = [
        {
            "event_id": e.event_id,
            "session_id": e.session_id,
            "occurred_at": e.occurred_at,
            "game_time_seconds": e.game_time,
            "category": e.category,
            "event_type": e.event_type,
            "object_name": e.object_name,
        }
        for e in batch.events
    ]
    stmt = pg_insert(PlayerEvent).values(rows).on_conflict_do_nothing(
        index_elements=["event_id"]
    )
    result = db.execute(stmt)
    db.commit()
    return {"received": len(rows), "saved": result.rowcount}


@app.get("/events", response_model=list[EventOut])
def list_events(
    db: DbDep,
    admin: Annotated[User, Depends(get_admin)],
    session_id: UUID | None = None,
    category: str | None = None,
    since: datetime | None = None,
    limit: int = Query(100_000, le=500_000),
):
    query = select(PlayerEvent).order_by(PlayerEvent.occurred_at.desc()).limit(limit)
    if session_id:
        query = query.where(PlayerEvent.session_id == session_id)
    if category:
        query = query.where(PlayerEvent.category == category)
    if since:
        query = query.where(PlayerEvent.occurred_at >= since)
    return db.scalars(query).all()