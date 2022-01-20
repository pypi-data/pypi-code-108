from .backend import app

if app:

    @app.task(name="hello")
    def task_hello(name):
        return f"Hello {name}"
