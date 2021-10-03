from machine.resources import JsonRPCResource
from machine import start

from example.api.scopes import api


r = api.add_resource(JsonRPCResource(name='docs_v1', path=start/'docs'/'v2'))


@r.method
async def add(a, b):
    return a + b

