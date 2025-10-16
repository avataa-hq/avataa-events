from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database import get_session
from routers.event_router.processors import (
    GetEventsByFilters,
    GetParameterEventsByObjectIds,
)
from routers.event_router.schemas import (
    GetEventsByInstanceTypeRequest,
    GetEventsByInstanceTypeResponse,
    GetParameterHistoryByObjectIdsRequest,
)

event_router = APIRouter(tags=["Events"], prefix="/events")


@event_router.post(
    path="/get_events_by_filter",
    response_model=GetEventsByInstanceTypeResponse,
)
async def get_events_by_filter(
    request: Request,
    user_request: GetEventsByInstanceTypeRequest,
    session: Session = Depends(get_session),
):
    """
    This endpoint operates filtering and sorting for events

    - **Available attributes for filtering and sorting:**

        "event_type",
        "instance",
        "old_value",
        "new_value",
        "instance_id",
        "attribute",
        "valid_from",
        "valid_to",
        "is_active",

    - **Filter column format:**
        [{field: str,
          value: Any,
          condition: AND / OR}]
    """
    token = request.headers.get("Authorization")

    task = GetEventsByFilters(
        session=session, request=user_request, token=token
    )
    return task.execute()


@event_router.post(
    path="/get_parameter_by_object_ids",
    # response_model=GetParameterHistoryByObjectIdsResponse,
)
async def get_parameter_by_object_ids(
    request: Request,
    user_request: GetParameterHistoryByObjectIdsRequest,
    session: Session = Depends(get_session),
):
    task = GetParameterEventsByObjectIds(
        session=session,
        request=user_request,
        token=request.headers.get("Authorization"),
    )
    return task.execute()
