import logging

from machine import Machine

from example.api.scopes import api

logger = logging.getLogger(__name__)


app = Machine()

app.add_root(api)


@app.on_startup
async def say_hi(_):
    logger.info('App is starting/restarting...')


@app.on_shutdown
async def say_bye(_):
    logger.info('App is shutting down...')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, log_level='info')
