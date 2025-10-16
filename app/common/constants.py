from enum import Enum


class DescendingOrders(Enum):
    ASC = "ASC"
    DESC = "DESC"


class ConditionsOrders(Enum):
    AND = "AND"
    OR = "OR"


AVAILABLE_COLUMNS_FOR_EVENTS = {
    "event_type",
    "instance",
    "old_value",
    "new_value",
    "instance_id",
    "attribute",
    "valid_from",
    "valid_to",
    "is_active",
    "user_id",
    "session_id",
}


class EventType(str, Enum):
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    CREATED = "CREATED"
    ARCHIVED = "ARCHIVED"


class InventoryChangesIndexes(Enum):
    TMO = "event_manager_object_type"
    MO = "event_manager_object"
    TPRM = "event_manager_parameter_type"
    PRM = "event_manager_parameter"
    ALL = "event_manager*"


EVENT_INDEXES_BY_INSTANCES = dict(
    TMO="event_manager_object_type",
    MO="event_manager_object",
    TPRM="event_manager_parameter_type",
    PRM="event_manager_parameter",
    ALL="event_manager*",
)

INSTANCE_BY_EVENT_MANAGER_INDEX = {
    InventoryChangesIndexes.TMO.value: "TMO",
    InventoryChangesIndexes.MO.value: "MO",
    InventoryChangesIndexes.TPRM.value: "TPRM",
    InventoryChangesIndexes.PRM.value: "PRM",
}
