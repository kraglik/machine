import pytest

from machine import Machine, start, end, slug, Request, Response
from machine.resources import RESTResource, JsonRPCResource

app = Machine()

api = app.scope(start/'api')

v1 = api.scope(start/'v1')
v2 = api.scope(start/'v2')


@v1.resource('echo', start/'echo' + end)
class EchoResourceV1(RESTResource):
    async def post(self, request: Request):
        return Response(
            body=await request.body(),
            status_code=200,
            content_type=request.content_type
        )


@v1.resource('name', start/'name'/slug('name') + end)
class NameResourceV1(RESTResource):
    async def get(self, request: Request, name: str) -> Response:
        return Response.text(name, status_code=200)


rpc = v2.add_resource(JsonRPCResource('json_rpc', start/'public'/'jsonrpc'))


@rpc.method
async def echo(*args, **kwargs):
    return kwargs


@pytest.fixture
def client(test_client_factory):
    with test_client_factory(app) as client:
        yield client


def test_router(client):
    response = client.get("/")
    assert response.status_code == 404

    response = client.post("/api/v1/echo", json={'hello': 'world'})
    assert response.status_code == 200
    assert response.json() == {'hello': 'world'}

    response = client.get("/api/v1/echo", json={'hello': 'world'})
    assert response.status_code == 405

    response = client.get("/api/v1/echo")
    assert response.status_code == 405

    response = client.get("/foo")
    assert response.status_code == 404

    response = client.get("/api/v1/name/machine")
    assert response.status_code == 200
    assert response.text == 'machine'

