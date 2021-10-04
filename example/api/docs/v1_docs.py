from machine.resources import RESTResource
from machine import Request, Response

from example.api.scopes import api


@api.resource(name='docs_v1', path='/docs/v1')
class APIV1Docs(RESTResource):
    async def get(self, request: Request) -> Response:
        return Response.html(
            body="""
                <h1>Docs for API v.1</h1>
                <h3>No docs yet</h3>
            """,
            status_code=200
        )

