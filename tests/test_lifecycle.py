import pytest

from machine import Machine, start

app = Machine()

api = app.scope(start/'api')


class StateTracker:
    def __init__(self):
        self.__started = False
        self.__shutdown = False

    def start(self):
        self.__started = True

    def stop(self):
        self.__shutdown = True

    def reset(self):
        self.__started = False
        self.__shutdown = False

    @property
    def started(self):
        return self.__started

    @property
    def shutdown(self):
        return self.__shutdown


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
