import asyncio
import json
import logging

import grpc

from common.exceptions import NotAvailableInstanceType
from services.event_processor.inventory_processor.processor import (
    ObjectTypeEventProcessor,
    ObjectEventProcessor,
    ParameterTypeEventProcessor,
    ParameterEventProcessor,
)
from services.grpc_service.proto_files.event_manager_methods.files import (
    event_manager_pb2_grpc,
    event_manager_pb2,
)


class EventManagerInformer(event_manager_pb2_grpc.EventManagerInformerServicer):
    def _get_adapter_for_process(self, instance_type: str):
        match instance_type:
            case "TMO":
                return ObjectTypeEventProcessor()
            case "MO":
                return ObjectEventProcessor()
            case "TPRM":
                return ParameterTypeEventProcessor()
            case "PRM":
                return ParameterEventProcessor()
            case _:
                raise NotAvailableInstanceType(
                    f"Instance {instance_type} does not available"
                )

    def _process_event(self, request):
        adapter = self._get_adapter_for_process(request.instance_name)
        print(json.loads(request.data))
        adapter.process(
            instances=[json.loads(request.data)],
            event_type=request.type,
            user_id=None,
            session_id=None,
            instance_type=request.instance_name,
        )

    def NewEvent(
        self,
        request_iterator,
        context: grpc.ServicerContext,
    ):
        for request in request_iterator:
            self._process_event(request)
            yield event_manager_pb2.NewEventResponse(
                is_success=True, message="Accepted"
            )


async def start_grpc_serve() -> None:
    # Keepalive options for server https://github.com/grpc/grpc/blob/master/examples/python/keep_alive/greeter_server.py
    server_options = [
        ("grpc.keepalive_time_ms", 10_000),
        ("grpc.keepalive_timeout_ms", 15_000),
        ("grpc.http2.min_ping_interval_without_data_ms", 5_000),
        ("grpc.max_connection_idle_ms", 2_147_483_647),
        ("grpc.max_connection_age_ms", 3_600_000 * 24),
        ("grpc.max_connection_age_grace_ms", 5_000),
        ("grpc.http2.max_pings_without_data", 5),
        ("grpc.keepalive_permit_without_calls", 1),
    ]
    port = 50051
    listen_addr = "[::]:" + str(port)

    server = grpc.aio.server(options=server_options)

    event_manager_pb2_grpc.add_EventManagerInformerServicer_to_server(
        EventManagerInformer(), server
    )

    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_grpc_serve())
