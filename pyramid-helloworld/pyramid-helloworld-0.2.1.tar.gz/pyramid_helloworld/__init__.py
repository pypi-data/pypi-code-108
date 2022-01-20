import pkg_resources

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.router import Router

__version__ = pkg_resources.get_distribution("pyramid-helloworld").version

from .backend import app
from . import tasks


def hello_world(request):
    return Response("Hello World!")


def hello_celery(request):
    return Response(
        tasks.task_hello.delay(request.GET.get("name", "World!")).get()
    )


def main(global_config: dict, **settings) -> Router:
    """Build the pyramid WSGI App."""

    with Configurator(settings=settings) as config:
        if app:
            config.include("celery_yaml")
        config.add_route("root", "/")
        config.add_route("celery", "/celery")

        config.add_view(hello_world, route_name="root")
        if app:
            config.add_view(hello_celery, route_name="celery")

        return config.make_wsgi_app()
