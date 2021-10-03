from machine import Scope, start

api = Scope(start/'api')

api_v1 = api.scope(start/'v1')
api_v2 = api.scope(start/'v2')
