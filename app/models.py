import uuid
from datetime import datetime

from sqlalchemy.ext.declarative import (
    declarative_base,
)
from sqlmodel import SQLModel, Field

from common.constants import EventType

Base = declarative_base(metadata=SQLModel.metadata)


class EventsBase(SQLModel):
    event_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    event_type: EventType = Field(nullable=False)
    instance: str = Field(nullable=False)
    old_value: str = Field(nullable=True)
    new_value: str = Field(nullable=True)
    instance_id: int = Field(nullable=False)
    user_id: str = Field(nullable=True)
    attribute: str = Field(nullable=False)
    version: int = Field(nullable=False)
    valid_from: datetime = Field(
        default_factory=datetime.utcnow, nullable=False
    )
    valid_to: datetime = Field(nullable=True)
    is_active: bool = Field(nullable=False, default=True)


class InventoryEvents(EventsBase, table=True):
    session_id: str = Field(nullable=True, default=None)
