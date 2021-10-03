from machine.resources import RESTResource
from machine import start, slug, end, Connection

from example.api.scopes import api_v1
from machine.response import html_response


@api_v1.resource(name='hello', path=start/'hello'/slug('name') + end)
class HelloResource(RESTResource):
    async def get(self, conn: Connection, params: dict):

        conn.put_cookie('some_token', b'blahblah')
        conn.put_header('Authorization', b'Bearer something')

        return html_response(
            status_code=200,
            body=f"<h1>Hello, {params['name']}</h1>"
        )


@api_v1.resource(name='echo', path=start/'echo' + end)
class EchoResource(RESTResource):
    async def post(self, conn: Connection, params: dict):
        body = await conn.body()

        content_type = conn.headers['content-type']

        await conn.send_head(
            content_type=content_type.decode('utf-8'),
            status_code=200,
            headers=[]
        )
        await conn.send_body(body)
