import pytest

from machine import Machine

app = Machine()

api = app.scope('/api')


class StateTracker:
    def __init__(self):
        self._started = False
        self._shutdown = False

    def start(self):
        self._started = True

    def stop(self):
        self._shutdown = True

    def reset(self):
        self._started = False
        self._shutdown = False

    @property
    def started(self):
        return self._started

    @property
    def shutdown(self):
        return self._shutdown


def test_lifecycle(test_client_factory):
    tracker = StateTracker()

    @app.on_startup
    async def change_startup_done(_):
        tracker.start()

    @app.on_shutdown
    async def change_shutdown_done(_):
        tracker.stop()

    tracker.reset()

    with test_client_factory(app) as client:
        response = client.get("/")
        assert response.status_code == 404

    assert tracker.started
    assert tracker.shutdown
