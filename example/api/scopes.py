from machine.plugins.rest import DefaultErrorRenderer, rest_error_plugin
from machine.plugins import options, sequence, path

from example.api.v1.rest import todo_r, name_r
from example.api.v2.jsonrpc import public

api_v1 = sequence(
    [
        path("/v1"),
        options(
            [
                sequence([path("/todo$"), todo_r]),
                sequence([path("/todos/{name}$"), name_r]),
            ]
        ),
    ]
)

api_v2 = sequence(
    [path("/v2"), options([sequence([path("/public/jsonrpc$"), public])])]
)


api = sequence(
    [
        rest_error_plugin(DefaultErrorRenderer()),
        path("/api"),
        options([api_v1, api_v2]),
    ]
)
