from machine.resources import JsonRPCResource
from machine import start, slug

from example.api.scopes import api


r = api.add_resource(JsonRPCResource(name='docs_v1', path=start/'docs'/'v2'/slug('endpoint')))


@r.method
async def add(a: int, b: int, endpoint: str):
    return {
        "addition_result": a + b,
        "endpoint": endpoint
    }

