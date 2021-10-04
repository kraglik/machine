import pytest

from machine import Machine
from machine.resources import JsonRPCResource

app = Machine()

api = app.scope('/api')
rpc = api.add_resource(
    JsonRPCResource(
        'json_rpc',
        '/public/jsonrpc'
    )
)


@rpc.method
async def echo(*args, **kwargs):
    if len(args) == 1:
        return args[0]

    return kwargs


@rpc.method
async def add(a: int, b: int) -> int:
    return a + b


@pytest.fixture
def client(test_client_factory):
    with test_client_factory(app) as client:
        yield client


def test_jsonrpc(client):

    def jsonrpc_request(method_name: str, params) -> dict:
        return {
            "id": "1",
            "jsonrpc": "2.0",
            "method": method_name,
            "params": params
        }

    def jsonrpc_response(method_name: str, result) -> dict:
        return {
            "id": "1",
            "jsonrpc": "2.0",
            "method": method_name,
            "result": result
        }

    response = client.get("/api/public/jsonrpc")
    assert response.status_code == 405

    response = client.post(
        "/api/public/jsonrpc",
        json={
            'hello': 'world'
        }
    )
    assert response.status_code == 400

    response = client.post(
        "/api/public/jsonrpc",
        json=jsonrpc_request('echo', {'hello': 'world'})
    )
    assert response.status_code == 200
    assert response.json() == jsonrpc_response('echo', {'hello': 'world'})

    response = client.post(
        "/api/public/jsonrpc",
        json=jsonrpc_request('echo', 1)
    )
    assert response.status_code == 200
    assert response.json() == jsonrpc_response('echo', 1)

