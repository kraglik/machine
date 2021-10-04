from machine import Scope, start
from machine.plugins import resource
from machine.pipelines import api_pipeline, browser_pipeline

from example.infrastructure.db.session import session_constructor, session_destructor

api = Scope(start/'api')

api_v1 = api.scope(start/'v1')
api_v1.pipeline([
    browser_pipeline,
    resource(
        name='db',
        constructor=session_constructor,
        destructor=session_destructor
    )
])

api_v2 = api.scope(start/'v2')
api_v2.pipeline([
    api_pipeline  # Plugin api allows pipelines to be included in other pipelines
])
