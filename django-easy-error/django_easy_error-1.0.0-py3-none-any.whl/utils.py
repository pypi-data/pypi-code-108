"""The django rendering logic is wrapped to ensure the correct HTML templates
are included rendered for each error code."""

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template


def error_render(error_code: int, request: HttpRequest) -> HttpResponse:
    """Render the appropriate error template for the given error code

    Args:
        error_code: The HTTP error code to render a response for
        request: The incoming HTTP request

    Returns:
        A rendered HTTP response
    """

    try:
        template = f'simple_error/http_{error_code}.html'
        get_template(template)

    except TemplateDoesNotExist:
        template = 'simple_error/default.html'

    context = {
        'error_code': error_code,
        'description': settings.ERROR_CODE_DESCRIPTIONS[error_code],
        'description_long': settings.ERROR_CODE_DESCRIPTIONS_LONG[error_code]
    }

    return render(request, template, status=error_code, context=context)
