import json

from resistant_kafka_avataa import (
    ConsumerInitializer,
    ConsumerConfig,
    kafka_processor,
)
from resistant_kafka_avataa.message_desirializers import MessageDeserializer

from common.exceptions import NotAvailableInstanceType
from services.event_processor.inventory_processor.processor import (
    ParameterEventProcessor,
    ObjectTypeEventProcessor,
    ParameterTypeEventProcessor,
    ObjectEventProcessor,
)


class InventoryChangesProcessor(ConsumerInitializer):
    def __init__(
        self, config: ConsumerConfig, deserializers: MessageDeserializer
    ):
        super().__init__(config=config, deserializers=deserializers)
        self._config = config

    @staticmethod
    def _get_adapter_for_process(instance_type: str):
        match instance_type:
            case "TMO":
                adapter = ObjectTypeEventProcessor()

            case "MO":
                adapter = ObjectEventProcessor()

            case "TPRM":
                adapter = ParameterTypeEventProcessor()

            case "PRM":
                adapter = ParameterEventProcessor()

            case _:
                raise NotAvailableInstanceType(
                    f"Instance {instance_type} does not available"
                )

        return adapter

    @staticmethod
    def _get_user_id_from_message_headers(
        message_headers: dict,
    ) -> str | None:
        user_id = message_headers.get("user_id")
        return user_id.decode("utf-8") if user_id else None

    @staticmethod
    def _get_session_id_from_message_headers(
        message_headers: dict,
    ) -> str | None:
        session_id = message_headers.get("session_id")
        return session_id.decode("utf-8") if session_id else None

    @kafka_processor(store_error_messages=False)
    async def process(self, message):
        instance_type, event_type = message.key().decode("utf-8").split(":")
        message_headers = dict(message.headers())

        user_id = self._get_user_id_from_message_headers(
            message_headers=message_headers
        )
        session_id = self._get_session_id_from_message_headers(
            message_headers=message_headers
        )

        instances = self._deserializers.deserialize_to_dict(message=message)[
            "objects"
        ]

        adapter = self._get_adapter_for_process(instance_type=instance_type)
        adapter.process(
            instances=instances,
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            instance_type=instance_type,
        )


class EventChangesProcessor(ConsumerInitializer):
    def __init__(
        self, config: ConsumerConfig, deserializers: MessageDeserializer
    ):
        super().__init__(config=config, deserializers=deserializers)
        self._config = config

    @staticmethod
    def _get_adapter_for_process(instance_type: str):
        match instance_type:
            case "TMO":
                adapter = ObjectTypeEventProcessor()

            case "MO":
                adapter = ObjectEventProcessor()

            case "TPRM":
                adapter = ParameterTypeEventProcessor()

            case "PRM":
                adapter = ParameterEventProcessor()

            case _:
                raise NotAvailableInstanceType(
                    f"Instance {instance_type} does not available"
                )

        return adapter

    @staticmethod
    def _get_user_id_from_message_headers(
        message_headers: dict,
    ) -> str | None:
        user_id = message_headers.get("user_id")
        return user_id.decode("utf-8") if user_id else None

    @staticmethod
    def _get_session_id_from_message_headers(
        message_headers: dict,
    ) -> str | None:
        session_id = message_headers.get("session_id")
        return session_id.decode("utf-8") if session_id else None

    @kafka_processor(store_error_messages=False)
    async def process(self, message):
        instance_type, event_type = message.key().decode("utf-8").split(":")
        message_headers = dict(message.headers())
        user_id = self._get_user_id_from_message_headers(
            message_headers=message_headers
        )
        session_id = self._get_session_id_from_message_headers(
            message_headers=message_headers
        )
        instances = json.loads(message.value().decode("utf-8"))
        adapter = self._get_adapter_for_process(instance_type=instance_type)
        adapter.process(
            instances=instances,
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
        )
