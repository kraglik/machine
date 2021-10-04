import pytest

from machine import Machine, start, end
from machine.resources import JsonRPCResource

app = Machine()

api = app.scope(start/'api' + end)
rpc = api.add_resource(
    JsonRPCResource(
        'json_rpc',
        start/'public/jsonrpc'
    )
)


@rpc.method
async def echo(*args, **kwargs):
    return kwargs


@rpc.method
async def add(a: int, b: int) -> int:
    return a + b


@pytest.fixture
def client(test_client_factory):
    with test_client_factory(app) as client:
        yield client


def test_router(client):
    response = client.get("/api/public/jsonrpc")
    assert response.status_code == 405

    response = client.post(
        "/api/public/jsonrpc",
        json={
            'hello': 'world'
        }
    )
    assert response.status_code == 400

