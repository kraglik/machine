# Machine
A very simple web framework implemented in Python.

The core idea of this framework are **plugins**.
Plugins could be found everywhere throughout the framework.
Plugin itself is simple - it's just an asynchronous generator that yields a tuple of `Connection` and `Parameters`.

The simplest possible plugin just yields its arguments:
```python3
async def simple_plugin(conn, params):
    yield conn, params
```



# Installation

To install Machine, just type `pip install machine-web` in your console.
