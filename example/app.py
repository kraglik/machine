from machine import Machine

from example.api.scopes import api, api_v1, api_v2
from example.api.docs.v1_docs import APIV1Docs
from example.api.docs.v2_docs import APIV2Docs
from example.api.v1.rest import HelloResource
from example.api.v2.rest import SimpleHelloResource


app = Machine()

app.add_scope(api)
app.add_scope(api_v1)
app.add_scope(api_v2)


@app.on_startup
async def say_hi(_):
    print('Hi!')


@app.on_shutdown
async def say_bye(_):
    print('Bye!')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, log_level='info')
