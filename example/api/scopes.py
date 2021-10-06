from machine.plugins import options, sequence, path

from example.api.v1.rest import todo_r, name_r

api_v1 = sequence([
    path('/v1'),
    options([
        todo_r,
        name_r
    ])
])


api = sequence([
    path('/api'),
    options([
        api_v1
    ])
])
