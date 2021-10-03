from machine import Machine
from machine import start, end, slug, const

from example.api.scopes import api, api_v1, api_v2
from example.api.docs.v1_docs import r as v1_docs_resource
from example.api.docs.v2_docs import r as v2_docs_resource
from example.api.v1.rest import HelloResource


app = Machine()

app.add_scope(api)
app.add_scope(api_v1)
app.add_scope(api_v2)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, log_level='info')
