from machine import Scope, Pipeline
from machine.plugins import resource

from example.infrastructure.db.session import session_constructor, session_destructor

api = Scope('/api')
api.pipeline([
    resource(
        name='db',
        constructor=session_constructor,
        destructor=session_destructor
    )
])
