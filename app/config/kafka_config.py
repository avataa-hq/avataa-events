import os

AVAILABLE_TRUE_VALUES = ["TRUE", "Y", "YES", "1"]

KAFKA_TURN_ON = (
    str(os.environ.get("KAFKA_TURN_ON", True)).upper() in AVAILABLE_TRUE_VALUES
)
KAFKA_SECURED = (
    str(os.environ.get("KAFKA_SECURED", False)).upper() in AVAILABLE_TRUE_VALUES
)

KAFKA_URL = os.environ.get("KAFKA_URL", "kafka:9092")
KAFKA_CONSUMER_GROUP_ID = os.environ.get(
    "KAFKA_CONSUMER_GROUP_ID", "Event_Manager"
)
KAFKA_CONSUMER_OFFSET = os.environ.get("KAFKA_CONSUMER_OFFSET", "latest")
KAFKA_SUBSCRIBE_TOPICS = os.environ.get(
    "KAFKA_SUBSCRIBE_TOPICS", "inventory.changes"
)
KAFKA_EVENT_CHANGES_TOPICS = os.environ.get(
    "KAFKA_EVENT_CHANGES_TOPICS", "event_migrate"
)

KAFKA_KEYCLOAK_SCOPES = os.environ.get("KAFKA_KEYCLOAK_SCOPES", "profile")
KAFKA_KEYCLOAK_CLIENT_ID = os.environ.get("KAFKA_KEYCLOAK_CLIENT_ID", "kafka")

KAFKA_KEYCLOAK_CLIENT_SECRET = os.environ.get(
    "KAFKA_KEYCLOAK_CLIENT_SECRET", ""
)
KAFKA_KEYCLOAK_TOKEN_URL = os.environ.get(
    "KAFKA_KEYCLOAK_TOKEN_URL",
    "http://keycloak:8080/realms/avataa/protocol/openid-connect/token",
)

KAFKA_SCHEMA_REGISTRY_URL = os.environ.get(
    "KAFKA_SCHEMA_REGISTRY_URL", "http://schema-registry:8081"
)

KAFKA_SECURITY_PROTOCOL = "SASL_PLAINTEXT"
KAFKA_SASL_MECHANISMS = "OAUTHBEARER"
