from machine import Pipeline
from machine.plugins import accepts

browser_pipeline = Pipeline([
    accepts('html')
])
