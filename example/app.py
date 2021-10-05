import logging

from machine import Machine

from example.api.scopes import api
from example.api.v1.rest import todo_r
from example.api.v1.jsonrpc import rpc

logger = logging.getLogger(__name__)


app = Machine()

app.add(api)


@app.on_startup
async def say_hi(_):
    logger.info('App is starting/restarting...')


@app.on_shutdown
async def say_bye(_):
    logger.info('App is shutting down...')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, log_level='info')
