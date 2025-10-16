from datetime import datetime, timezone
from typing import Any

from common.constants import EventType
from services.event_processor.inventory_processor.constants import (
    DATETIME_FORMAT,
)


def remove_items_from_dict_by_list(instance: dict, keys_to_remove: set[str]):
    copy_instance = dict(instance)
    for stop_attribute in keys_to_remove:
        if copy_instance.get(stop_attribute):
            del copy_instance[stop_attribute]

    return copy_instance


def get_value_from_enum(value: Any) -> str:
    if hasattr(value, "value"):
        return value.value

    if isinstance(value, str):
        return value

    raise ValueError(f"Unsupported enum/str value: {value!r}")


def format_event_type(event_type: EventType | str) -> str:
    val = get_value_from_enum(event_type)
    return val.upper()


def prepare_datetime_for_convert(date_request: Any) -> datetime | None:
    if not date_request or not isinstance(date_request, str):
        return None

    try:
        if date_request.endswith("Z"):
            dt = datetime.fromisoformat(date_request.replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc).replace(tzinfo=None)

        dt = datetime.fromisoformat(date_request)
        if dt.tzinfo:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt

    except (ValueError, TypeError):
        return None


def convert_datetime_by_format(date_request: datetime | None) -> str:
    if not date_request:
        date_request = datetime(1970, 1, 1)

    return date_request.strftime(DATETIME_FORMAT)


def format_recording_datetime(
    instance: dict,
    *,
    attribute: str,
    base_attribute: str | None = None,
    use_now_if_missing: bool = False,
) -> str:
    dt = prepare_datetime_for_convert(date_request=instance.get(attribute))

    if not dt and base_attribute:
        dt = prepare_datetime_for_convert(
            date_request=instance.get(base_attribute)
        )

    if not dt and use_now_if_missing:
        dt = datetime.utcnow()

    return convert_datetime_by_format(date_request=dt)


def generate_record_id(
    *, instance_id: Any, attribute: str, version: int, event_type: str
) -> str:
    return f"{instance_id}:{attribute}:{version}:{event_type}"


def compare_values_equal(a: Any, b: Any) -> bool:
    if type(a) is type(b):
        return a == b

    return str(a) == str(b)
