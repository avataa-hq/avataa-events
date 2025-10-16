from fastapi.middleware.cors import CORSMiddleware

import database  # noqa
from config import app_config
from config.app_config import APP_PREFIX, APP_VERSION
from config.kafka_config import (
    KAFKA_TURN_ON,
)
from create_fastapi_app import create_app
from routers.event_router.router import event_router
from services.elastic_service.elastic_client import (
    create_basic_indexes_if_not_exists,
)
from services.kafka_service.kafka_connection_utils import (
    start_kafka_consumer,
)

app = create_app(root_path=APP_PREFIX)

if app_config.DEBUG:
    app.debug = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app_v1 = create_app(root_path=f"{APP_PREFIX}/v{APP_VERSION}")

app.mount(path=f"/v{APP_VERSION}", app=app_v1)

app_v1.include_router(event_router)


@app.on_event("startup")
async def on_startup():
    if KAFKA_TURN_ON:
        start_kafka_consumer()

    create_basic_indexes_if_not_exists()
