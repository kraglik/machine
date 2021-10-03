from machine.resources import JsonRPCResource
from machine import start

from example.api.scopes import api


r = api.add_resource(JsonRPCResource(name='docs_v1', path=start/'docs'/'v1'))


@r.method
async def echo(*args, **kwargs):
    return kwargs

