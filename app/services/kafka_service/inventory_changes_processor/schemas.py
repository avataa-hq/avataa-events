from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from models import EventType


class EventsBase(BaseModel):
    event_type: EventType
    old_value: Any | None = None
    new_value: Any | None = None
    user_id: str | None = None
    session_id: str | None = None
    instance_id: int
    attribute: str
    version: int
    valid_to: datetime | str | None = None
    is_active: bool = True
    valid_from: datetime | str = Field(default_factory=datetime.utcnow)
