from machine import Pipeline
from machine.plugins import content_type

api_pipeline = Pipeline([
    content_type('application/json')
])
