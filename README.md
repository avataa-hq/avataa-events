# Event Manager

## Environment variables

```toml
DB_HOST=<pgbouncer/postgres_host>
DB_NAME=<pgbouncer/postgres_event_manager_db_name>
DB_PASS=<pgbouncer/postgres_event_manager_password>
DB_PORT=<pgbouncer/postgres_port>
DB_TYPE=postgresql
DB_USER=<pgbouncer/postgres_event_manager_user>
DEBUG=<True/False>
DOCS_CUSTOM_ENABLED=<True/False>
DOCS_REDOC_JS_URL=<redoc_js_url>
DOCS_SWAGGER_CSS_URL=<swagger_css_url>
DOCS_SWAGGER_JS_URL=<swagger_js_url>
ES_HOST=<elasticsearch_host>
ES_PASS=<elasticsearch_event_manager_password>
ES_PORT=<elasticsearch_port>
ES_PROTOCOL=<elasticsearch_protocol>
ES_USER=<elasticsearch_event_manager_user>
KAFKA_CONSUMER_GROUP_ID=Event_Manager
KAFKA_CONSUMER_OFFSET=latest
KAFKA_KEYCLOAK_CLIENT_ID=<kafka_client>
KAFKA_KEYCLOAK_CLIENT_SECRET=<kafka_client_secret>
KAFKA_KEYCLOAK_SCOPES=profile
KAFKA_KEYCLOAK_TOKEN_URL=<keycloak_protocol>://<keycloak_host>:<keycloak_port>/realms/avataa/protocol/openid-connect/token
KAFKA_SCHEMA_REGISTRY_URL=<schema_registry_protocol>://<schema_registry_host>:<schema_registry_port>
KAFKA_SECURED=<True/False>
KAFKA_SUBSCRIBE_TOPICS=inventory.changes
KAFKA_TURN_ON=<True/False>
KAFKA_URL=<kafka_host>:<kafka_port>
KEYCLOAK_CLIENT_ID=<event_manager_client>
KEYCLOAK_CLIENT_SECRET=<event_manager_client_secret>
KEYCLOAK_HOST=<keycloak_host>
KEYCLOAK_PORT=<keycloak_port>
KEYCLOAK_PROTOCOL=<keycloak_protocol>
KEYCLOAK_REALM=avataa
KEYCLOAK_REDIRECT_HOST=<keycloak_external_host>
KEYCLOAK_REDIRECT_PORT=<keycloak_external_port>
KEYCLOAK_REDIRECT_PROTOCOL=<keycloak_external_protocol>
OPA_HOST=<opa_host>
OPA_POLICY=main
OPA_PORT=<opa_port>
OPA_PROTOCOL=<opa_protocol>
SECURITY_MIDDLEWARE_HOST=<security_middleware_host>
SECURITY_MIDDLEWARE_PORT=<security_middleware_port>
SECURITY_MIDDLEWARE_PROTOCOL=<security_middleware_protocol>
SECURITY_TYPE=<security_type>
```

### Explanation

#### Compose

- `REGISTRY_URL` - Docker regitry URL, e.g. `harbor.domain.com`
- `PLATFORM_PROJECT_NAME` - Docker regitry project Docker image can be downloaded from, e.g. `avataa`