from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator


class EventIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event_id: UUID = Field(alias="eventId")
    session_id: UUID = Field(alias="sessionId")
    occurred_at: AwareDatetime = Field(alias="occurredAt")  # exige fuso horário
    game_time: float = Field(alias="gameTime", ge=0)
    category: Literal["interaction", "movement"]
    event_type: str = Field(alias="type", min_length=1, max_length=50)
    object_name: str | None = Field(default=None, alias="objectName", max_length=100)

    @field_validator("object_name")
    @classmethod
    def empty_to_none(cls, v):
        return v or None  # Unity manda "" nos movimentos


class EventBatch(BaseModel):
    events: list[EventIn] = Field(min_length=1, max_length=500)


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: UUID
    occurred_at: AwareDatetime
    game_time_seconds: float
    category: str
    event_type: str
    object_name: str | None


class Token(BaseModel):
    access_token: str
    token_type: str