import asyncio
import logging

import grpc
from grpc.aio import Channel
from proto_files.event_manager_methods.files import (
    event_manager_pb2_grpc,
    event_manager_pb2,
)


async def create_object_event(channel: Channel):
    stub = event_manager_pb2_grpc.EventManagerInformerStub(channel)
    msg = event_manager_pb2.ListMOWithSecurity(
        objects=..., user_id=..., event_type=...
    )
    grpc_response = stub.CreateObjectTypeEvent(msg)
    print(grpc_response)


async def main():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        await create_object_event(channel=channel)


if __name__ == "__main__":
    logging.basicConfig()
    asyncio.run(main())
