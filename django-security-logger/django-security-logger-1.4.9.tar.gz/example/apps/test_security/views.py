from django.http import HttpResponse

from security.throttling.validators import PerRequestThrottlingValidator
from security.logging.requests.utils import log_input_request_with_data
from security.decorators import hide_request_body, log_exempt, throttling_exempt, throttling
from security import requests


def proxy_view(request):
    return HttpResponse(
        requests.get(
            request.GET['url'],
            slug='proxy',
            related_objects=(request.user,) if request.user.is_authenticated else ()
        ).content
    )


@hide_request_body()
def hide_request_body_view(request):
    return HttpResponse()


@log_exempt()
def log_exempt_view(request):
    return HttpResponse()


@throttling_exempt()
def throttling_exempt_view(request):
    return HttpResponse()


@throttling(PerRequestThrottlingValidator(60, 1))
def extra_throttling_view(request):
    return HttpResponse()


def error_view(request):
    raise RuntimeError


def home_view(request):
    if request.user.is_authenticated:
        log_input_request_with_data(
            request, slug='user-home', extra_data={'user_pk': request.user.pk}, related_objects=[request.user]
        )
    return HttpResponse('home page response')
