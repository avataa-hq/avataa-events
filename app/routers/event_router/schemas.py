from datetime import datetime
from typing import List, Any

from pydantic import BaseModel, validator

from common.constants import (
    DescendingOrders,
    ConditionsOrders,
    AVAILABLE_COLUMNS_FOR_EVENTS,
)


class FilterColumn(BaseModel):
    field: str
    value: Any
    condition: ConditionsOrders = ConditionsOrders.AND

    @validator("field")
    @classmethod
    def validate_field(cls, field_value):
        if field_value in AVAILABLE_COLUMNS_FOR_EVENTS:
            return field_value

        raise ValueError(
            f"{field_value} is not valid for available "
            f"list of attributes: {AVAILABLE_COLUMNS_FOR_EVENTS}"
        )


class SortBy(BaseModel):
    field: str
    descending: DescendingOrders

    @validator("field")
    @classmethod
    def validate_field(cls, field_value):
        if field_value in AVAILABLE_COLUMNS_FOR_EVENTS:
            return field_value

        raise ValueError(
            f"{field_value} is not valid for available "
            f"list of attributes: {AVAILABLE_COLUMNS_FOR_EVENTS}"
        )


class GetEventsByInstanceTypeRequest(BaseModel):
    filter_column: List[FilterColumn] = []
    sort_by: SortBy = SortBy(
        field="valid_from", descending=DescendingOrders.DESC.value
    )
    date_to: datetime | None = None
    date_from: datetime | None = None
    limit: int = 10
    offset: int = 0


class GetEventsByInstanceTypeData(BaseModel):
    event_type: str
    instance: str | None
    old_value: Any | None
    new_value: Any | None
    instance_id: int
    attribute: str
    version: int
    user_id: str | None
    session_id: str | None
    valid_from: str
    valid_to: str | None
    is_active: bool


class GetEventsByInstanceTypeResponse(BaseModel):
    data: List[GetEventsByInstanceTypeData]
    total: int


class GetParameterHistoryByObjectIdsRequest(BaseModel):
    date_to: datetime | None = None
    date_from: datetime | None = None
    limit: int = 10
    offset: int = 0
    object_ids: List[int]
    sort_by_datetime: DescendingOrders = DescendingOrders.DESC


class ParameterHistoryByObjectIds(BaseModel):
    event_type: str
    old_value: Any
    new_value: Any
    instance_id: int
    attribute: str
    user_id: str
    valid_from: str
    valid_to: str | None
    parameter_type_id: int | None
    session_id: str | None


class GetParameterHistoryByObjectIdsResponse(BaseModel):
    data: dict[int, ParameterHistoryByObjectIds]
    total: int


class CreateEventRequest(BaseModel):
    instance: str
    data: list[dict]


class ElasticSearchResponse(BaseModel):
    response: list[dict]
    total_count: int
