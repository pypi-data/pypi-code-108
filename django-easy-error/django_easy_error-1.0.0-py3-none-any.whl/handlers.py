"""Handlers are used to process the routing of HTTP errors to the correct
template. Handler objects are provided for each of the error views supported by
Django."""

from django.http import HttpResponse, HttpRequest

from django_easy_error.utils import error_render

__all__ = ['handler400', 'handler403', 'handler404', 'handler500']


def handler400(request: HttpRequest, exception: int) -> HttpResponse:
    """Render a response to a 400 error"""

    return error_render(404, request)


def handler403(request: HttpRequest, exception: int) -> HttpResponse:
    """Render a response to a 403 error"""

    return error_render(404, request)


def handler404(request: HttpRequest, exception: int) -> HttpResponse:
    """Render a response to a 404 error"""

    return error_render(404, request)


def handler500(request: HttpRequest) -> HttpResponse:
    """Render a response to a 500 error"""

    return error_render(404, request)
