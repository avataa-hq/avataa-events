import asyncio
import logging
import time

import requests
from resistant_kafka_avataa.common_exceptions import TokenIsNotValid
from resistant_kafka_avataa.consumer import process_kafka_connection
from resistant_kafka_avataa.consumer_schemas import (
    ConsumerConfig,
    KafkaSecurityConfig,
)
from resistant_kafka_avataa.message_desirializers import MessageDeserializer

from config import kafka_config
from config.kafka_config import (
    KAFKA_SUBSCRIBE_TOPICS,
    KAFKA_URL,
    KAFKA_CONSUMER_GROUP_ID,
    KAFKA_CONSUMER_OFFSET,
    KAFKA_SECURED,
    KAFKA_SECURITY_PROTOCOL,
    KAFKA_SASL_MECHANISMS,
)
from services.grpc_service.proto_files.inventory_instances.files.inventory_instances_pb2 import (
    ListTMO,
    ListMO,
    ListPRM,
    ListTPRM,
)
from services.kafka_service.inventory_changes_processor.processor import (
    InventoryChangesProcessor,
)

logging.basicConfig(level=logging.INFO)


def get_token_for_kafka_by_keycloak(conf):
    logger = logging.getLogger(__name__)
    payload = {
        "grant_type": "client_credentials",
        "scope": str(kafka_config.KAFKA_KEYCLOAK_SCOPES),
    }

    attempt = 5
    while attempt > 0:
        try:
            response = requests.post(
                kafka_config.KAFKA_KEYCLOAK_TOKEN_URL,
                timeout=5,
                auth=(
                    kafka_config.KAFKA_KEYCLOAK_CLIENT_ID,
                    kafka_config.KAFKA_KEYCLOAK_CLIENT_SECRET,
                ),
                data=payload,
            )
        except ConnectionError:
            time.sleep(1)
            attempt -= 1

        else:
            if response.status_code == 200:
                token = response.json()
                expires_in = float(token["expires_in"]) * 0.9
                logger.debug(
                    f"{time.time()} Got new token. Attempt: {attempt} Expiration: {time.time() + expires_in}"
                )
                return token["access_token"], time.time() + expires_in

            time.sleep(1)
            attempt -= 1

    raise TokenIsNotValid("Token verification service unavailable")


def start_kafka_consumer():
    inventory_changes_config = ConsumerConfig(
        topic_to_subscribe=KAFKA_SUBSCRIBE_TOPICS,
        processor_name="InventoryChangesProcessor",
        bootstrap_servers=KAFKA_URL,
        group_id=KAFKA_CONSUMER_GROUP_ID,
        auto_offset_reset=KAFKA_CONSUMER_OFFSET,
        enable_auto_commit=False,
    )

    if KAFKA_SECURED:
        inventory_changes_config.security_config = KafkaSecurityConfig(
            oauth_cb=get_token_for_kafka_by_keycloak,
            security_protocol=KAFKA_SECURITY_PROTOCOL,
            sasl_mechanisms=KAFKA_SASL_MECHANISMS,
        )

    inventory_changes_deserializers = MessageDeserializer(
        topic=inventory_changes_config.topic_to_subscribe,
    )
    inventory_changes_deserializers.register_protobuf_deserializer(
        message_type=ListTMO
    )
    inventory_changes_deserializers.register_protobuf_deserializer(
        message_type=ListMO
    )
    inventory_changes_deserializers.register_protobuf_deserializer(
        message_type=ListTPRM
    )
    inventory_changes_deserializers.register_protobuf_deserializer(
        message_type=ListPRM
    )

    inventory_changes_processor = InventoryChangesProcessor(
        config=inventory_changes_config,
        deserializers=inventory_changes_deserializers,
    )

    asyncio.create_task(process_kafka_connection([inventory_changes_processor]))
