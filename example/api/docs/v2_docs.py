from machine.resources import RESTResource
from machine import Request, Response

from example.api.scopes import api


@api.resource(name='docs_v2', path='/docs/v2')
class APIV2Docs(RESTResource):
    async def get(self, request: Request) -> Response:
        return Response.html(
            body="""
                <h1>Docs for API v.2</h1>
                <h3>DOCS</h3>
            """,
            status_code=200
        )

