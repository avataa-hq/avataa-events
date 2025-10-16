from __future__ import annotations

from typing import Any, Iterable

from common.constants import InventoryChangesIndexes
from models import EventType
from services.converter_service.processor import ConvertParameterValues
from services.converter_service.schemas import ParameterInstance
from services.elastic_service.elastic_client import elastic_client
from services.event_processor.inventory_processor.constants import (
    AvailableInventoryInstances,
    INSTANCES_BATCH_SIZE,
)
from services.event_processor.inventory_processor.exceptions import (
    NotImplementedInstance,
    NotImplementedEventType,
)
from services.event_processor.inventory_processor.utils import (
    remove_items_from_dict_by_list,
    get_value_from_enum,
    format_event_type,
    generate_record_id,
    format_recording_datetime,
    compare_values_equal,
)
from services.kafka_service.inventory_changes_processor.schemas import (
    EventsBase,
)


class ElasticsearchBulkWriter:
    def __init__(self, index: str, batch_size: int = INSTANCES_BATCH_SIZE):
        self.index = index
        self.batch_size = batch_size
        self._actions: list[dict] = []

    def add_index(self, *, doc_id: str, document: dict) -> None:
        self._actions.append({"create": {"_index": self.index, "_id": doc_id}})
        self._actions.append(document)
        self.flush_on_limit()

    def add_update(self, *, doc_id: str, document: dict) -> None:
        self._actions.append({"update": {"_index": self.index, "_id": doc_id}})
        self._actions.append({"doc": document})
        self.flush_on_limit()

    def flush_on_limit(self):
        if len(self._actions) >= 2 * self.batch_size:
            self.flush()

    def flush(self) -> None:
        if not self._actions:
            return

        elastic_client.bulk(body=self._actions)
        self._actions.clear()


class InventoryAdapterFunction:
    def __init__(
        self,
        value: Any,
        key_class_name: AvailableInventoryInstances | str,
        event_type: EventType | str,
        user_id: str,
    ):
        self._value = value
        self._key_class_name = get_value_from_enum(value=key_class_name)
        self._event_type = event_type
        self._user_id = user_id

    def process(
        self, *, session_id: str | None, batch_size: int = INSTANCES_BATCH_SIZE
    ) -> None:
        match self._key_class_name:
            case AvailableInventoryInstances.TMO.value:
                adapter = ObjectTypeEventProcessor(batch_size=batch_size)

            case AvailableInventoryInstances.TPRM.value:
                adapter = ParameterTypeEventProcessor(batch_size=batch_size)

            case AvailableInventoryInstances.PRM.value:
                adapter = ParameterEventProcessor(batch_size=batch_size)

            case AvailableInventoryInstances.MO.value:
                adapter = ObjectEventProcessor(batch_size=batch_size)

            case _:
                raise NotImplementedInstance(
                    f"Unknown inventory instance: {self._key_class_name}"
                )

        adapter.process(
            instances=self._value,
            event_type=self._event_type,
            user_id=self._user_id,
            session_id=session_id,
            instance_type=self._key_class_name,
        )


class InventoryEventProcessor:
    def __init__(
        self,
        instance_name: AvailableInventoryInstances | str,
        stop_list_attributes: set[str],
        batch_size: int = INSTANCES_BATCH_SIZE,
    ):
        self._stop_list_attributes = stop_list_attributes
        self._instance_name = get_value_from_enum(instance_name)
        self._elastic_index = self._determine_index_for_store(
            self._instance_name
        )
        self._bulk = ElasticsearchBulkWriter(
            self._elastic_index, batch_size=batch_size
        )

    @staticmethod
    def check_required_attributes(instance: dict, instance_name: str) -> bool:
        required = {"id", "version"}

        if instance_name == AvailableInventoryInstances.PRM.value:
            required.add("value")

        return all(instance.get(attr) is not None for attr in required)

    @staticmethod
    def _determine_index_for_store(instance_name: str) -> str:
        mapping = {
            AvailableInventoryInstances.TMO.value: InventoryChangesIndexes.TMO.value,
            AvailableInventoryInstances.TPRM.value: InventoryChangesIndexes.TPRM.value,
            AvailableInventoryInstances.MO.value: InventoryChangesIndexes.MO.value,
            AvailableInventoryInstances.PRM.value: InventoryChangesIndexes.PRM.value,
        }
        try:
            return mapping[instance_name]

        except KeyError:
            raise NotImplementedInstance(
                f"Instance with name {instance_name} can't be determined"
            )

    @staticmethod
    def convert_parameter_value_by_val_type(instance: dict) -> None:
        try:
            task = ConvertParameterValues()
            instance["value"] = task.convert(
                parameter_instance=ParameterInstance(**instance)
            )
        except Exception as e:
            print(e)
            print("Can not convert parameter value")
            print(instance, "\n")

    def _create(self, instance: dict, user_id: str, session_id: str) -> None:
        _EVENT = EventType.CREATED.value
        is_prm = self._instance_name == AvailableInventoryInstances.PRM.value

        if is_prm:
            self.convert_parameter_value_by_val_type(instance)

        creation_date = format_recording_datetime(
            instance,
            attribute="creation_date",
            use_now_if_missing=is_prm,
        )

        for attribute, value in instance.items():
            if attribute in self._stop_list_attributes:
                continue

            new_event = EventsBase(
                event_type=_EVENT,
                new_value=value,
                instance_id=instance["id"],
                user_id=user_id,
                attribute=attribute,
                version=1,
                is_active=True,
                valid_from=creation_date,
                session_id=session_id,
            ).dict()

            self._bulk.add_index(
                doc_id=generate_record_id(
                    instance_id=instance["id"],
                    attribute=attribute,
                    version=1,
                    event_type=_EVENT,
                ),
                document=new_event,
            )

    def _update(self, instance: dict, user_id: str, session_id: str) -> None:
        _EVENT = EventType.UPDATED.value
        is_prm = self._instance_name == AvailableInventoryInstances.PRM.value

        if is_prm:
            self.convert_parameter_value_by_val_type(instance=instance)

        modification_date = format_recording_datetime(
            instance,
            attribute="modification_date",
            base_attribute="creation_date",
            use_now_if_missing=is_prm,
        )

        attributes_to_update = remove_items_from_dict_by_list(
            instance=instance, keys_to_remove=self._stop_list_attributes
        )

        query = {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"instance_id": instance["id"]}},
                        {"term": {"is_active": True}},
                        {
                            "terms": {
                                "attribute": list(attributes_to_update.keys())
                            }
                        },
                    ]
                }
            }
        }
        response = elastic_client.search(index=self._elastic_index, body=query)
        current_events_by_id: dict[str, dict] = {
            doc["_id"]: doc["_source"] for doc in response["hits"]["hits"]
        }

        processed_attributes: set[str] = set()

        for doc_id, old_attr in current_events_by_id.items():
            attribute = old_attr["attribute"]
            processed_attributes.add(attribute)

            new_val = attributes_to_update[attribute]
            if compare_values_equal(old_attr["new_value"], new_val):
                continue

            old_attr["valid_to"] = modification_date
            old_attr["is_active"] = False
            self._bulk.add_update(doc_id=doc_id, document=old_attr)

            next_version = (old_attr.get("version") or 0) + 1

            event_to_update = EventsBase(
                event_type=_EVENT,
                new_value=new_val,
                old_value=old_attr["new_value"],
                instance_id=instance["id"],
                user_id=user_id,
                attribute=attribute,
                version=next_version,
                is_active=True,
                valid_from=modification_date,
                session_id=session_id,
            ).dict()

            self._bulk.add_index(
                doc_id=generate_record_id(
                    instance_id=instance["id"],
                    attribute=attribute,
                    version=next_version,
                    event_type=_EVENT,
                ),
                document=event_to_update,
            )

        attributes_to_create = set(attributes_to_update.keys()).difference(
            processed_attributes
        )
        for attribute in attributes_to_create:
            new_event = EventsBase(
                event_type=_EVENT,
                new_value=attributes_to_update[attribute],
                instance_id=instance["id"],
                user_id=user_id,
                attribute=attribute,
                version=1,
                is_active=True,
                valid_from=modification_date,
                session_id=session_id,
            ).dict()

            new_id = generate_record_id(
                instance_id=instance["id"],
                attribute=attribute,
                version=1,
                event_type=_EVENT,
            )
            self._bulk.add_index(doc_id=new_id, document=new_event)

    def _delete(self, instance: dict, user_id: str, session_id: str) -> None:
        _EVENT = EventType.DELETED.value

        modification_date = format_recording_datetime(
            instance,
            attribute="modification_date",
            base_attribute="creation_date",
            use_now_if_missing=False,
        )

        query = {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"instance_id": instance["id"]}},
                        {"term": {"is_active": True}},
                    ]
                }
            }
        }
        response = elastic_client.search(index=self._elastic_index, body=query)
        attributes_to_update: dict[str, dict] = {
            doc["_id"]: doc["_source"] for doc in response["hits"]["hits"]
        }

        for doc_id, old_event in attributes_to_update.items():
            next_version = (old_event.get("version") or 0) + 1

            event_to_delete = EventsBase(
                event_type=_EVENT,
                old_value=old_event["new_value"],
                instance_id=instance["id"],
                user_id=user_id,
                attribute=old_event["attribute"],
                version=next_version,
                valid_from=modification_date,
                session_id=session_id,
            ).dict()

            self._bulk.add_index(
                doc_id=generate_record_id(
                    instance_id=instance["id"],
                    attribute=old_event["attribute"],
                    version=next_version,
                    event_type=_EVENT,
                ),
                document=event_to_delete,
            )

            old_event["valid_to"] = modification_date
            old_event["is_active"] = False
            self._bulk.add_update(doc_id=doc_id, document=old_event)

    def process(
        self,
        instances: Iterable[dict],
        event_type: EventType | str,
        user_id: str | None,
        session_id: str | None,
        instance_type: AvailableInventoryInstances | str,
    ) -> None:
        event_type = format_event_type(event_type)

        for instance in instances:
            if not self.check_required_attributes(
                instance=instance,
                instance_name=get_value_from_enum(instance_type),
            ):
                continue

            request = dict(
                instance=instance, user_id=user_id, session_id=session_id
            )

            match event_type:
                case EventType.CREATED.value:
                    self._create(**request)

                case EventType.UPDATED.value:
                    self._update(**request)

                case EventType.DELETED.value:
                    self._delete(**request)

                case _:
                    raise NotImplementedEventType(
                        f"Unsupported event type: {event_type}"
                    )

        self._bulk.flush()


class ObjectTypeEventProcessor(InventoryEventProcessor):
    def __init__(self, batch_size: int = INSTANCES_BATCH_SIZE) -> None:
        super().__init__(
            stop_list_attributes={
                "id",
                "creation_date",
                "modification_date",
                "version",
            },
            instance_name=AvailableInventoryInstances.TMO.value,
            batch_size=batch_size,
        )


class ObjectEventProcessor(InventoryEventProcessor):
    def __init__(self, batch_size: int = INSTANCES_BATCH_SIZE) -> None:
        super().__init__(
            stop_list_attributes={
                "id",
                "creation_date",
                "modification_date",
                "version",
            },
            instance_name=AvailableInventoryInstances.MO.value,
            batch_size=batch_size,
        )


class ParameterTypeEventProcessor(InventoryEventProcessor):
    def __init__(self, batch_size: int = INSTANCES_BATCH_SIZE) -> None:
        super().__init__(
            stop_list_attributes={
                "id",
                "creation_date",
                "modification_date",
                "version",
            },
            instance_name=AvailableInventoryInstances.TPRM.value,
            batch_size=batch_size,
        )


class ParameterEventProcessor(InventoryEventProcessor):
    def __init__(self, batch_size: int = INSTANCES_BATCH_SIZE) -> None:
        super().__init__(
            stop_list_attributes={"id"},
            instance_name=AvailableInventoryInstances.PRM.value,
            batch_size=batch_size,
        )
