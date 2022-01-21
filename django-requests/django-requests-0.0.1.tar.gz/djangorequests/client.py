import requests

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

DEFAULT_DISTRIBUTION = getattr(settings, "UESR_AGENT_DISTRIBUTION", "django-requests")


def user_agent(name):
    try:
        v = version(distribution_name=name)
    except PackageNotFoundError:
        v = "unknown"

    domain = get_current_site(None).domain
    ua = f"{name}/{v} (+{domain})"
    return ua


class DjangoSession(requests.Session):
    def __init__(self, distribution_name=DEFAULT_DISTRIBUTION):
        super().__init__()
        self.headers["user-agent"] = user_agent(distribution_name)


USER_AGENT = getattr(settings, "USER_AGENT", user_agent(DEFAULT_DISTRIBUTION))


def get(url, **kwargs):
    with DjangoSession() as s:
        return s.get(url, **kwargs)


def post(url, **kwargs):
    with DjangoSession() as s:
        return s.post(url, **kwargs)


def put(url, **kwargs):
    with DjangoSession() as s:
        return s.put(url, **kwargs)
