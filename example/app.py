import logging

from machine import Machine

from example.api.scopes import api

logger = logging.getLogger(__name__)


app = Machine()

app.root = api


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, log_level="info")
