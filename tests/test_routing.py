import pytest

from machine import Machine
from machine.plugins import sequence, options, path, RESTResource
from machine.plugins.rest import Request, Response, TextResponse
from machine.plugins.rest import rest_error_plugin, DefaultErrorRenderer

app = Machine()

v1echo = RESTResource()
v1name = RESTResource()


app.root = sequence([
    rest_error_plugin(DefaultErrorRenderer()),
    path('/api/v1'),
    options([
        sequence([
            path('/echo$'),
            v1echo
        ]),
        sequence([
            path('/name/{name}$'),
            v1name
        ])
    ])
])


@v1echo.post()
async def echo(request: Request):
    return Response(
        body=await request.body(),
        content_type=request.content_type
    )


@v1name.get()
async def show_name(request: Request) -> Response:
    return TextResponse(request.path_params['name'])


@pytest.fixture
def client(test_client_factory):
    with test_client_factory(app) as client:
        yield client


def test_router(client):
    response = client.get("/")
    assert response.status_code == 404

    response = client.get("/api/v1/echo", json={'hello': 'world'})
    assert response.status_code == 405

    response = client.get("/api/v1/echo")
    assert response.status_code == 405

    response = client.get("/foo")
    assert response.status_code == 404

    response = client.get("/api/v1/name/machine")
    assert response.status_code == 200
    assert response.text == 'machine'

