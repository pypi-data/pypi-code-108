import os

import pytest

try:
    import django
    from pytest_django.lazy_django import skip_if_no_django
    from pytest_django.live_server_helper import LiveServer
except ImportError:
    raise ImportError("pytest-django is required!")

__all__ = [
    'liveserver_ngrok_cls',
    'live_server_ngrok',
    'LiveServerNgrok',
    'LiveServerNgrokMixin'
]


class LiveServerNgrokMixin:
    def __init__(self, addr, ngrok):
        super().__init__(addr)
        self.ngrok = ngrok(port=self.thread.port)
        self.ngrok.init()

    @property
    def url(self):
        return self.ngrok.url

    def stop(self):
        super().stop()
        self.ngrok.stop()


class LiveServerNgrok(LiveServerNgrokMixin, LiveServer):
    pass


@pytest.fixture(scope='session')
def liveserver_ngrok_cls():
    return LiveServerNgrok


@pytest.fixture(scope='function')
def live_server_ngrok(request, liveserver_ngrok_cls, ngrok):
    """Run a live Django server in the background during tests
    and wrap with ngrok
    The address the server is started from is taken from the
    --liveserver command line option or if this is not provided from
    the DJANGO_LIVE_TEST_SERVER_ADDRESS environment variable.  If
    neither is provided ``localhost:8081,8100-8200`` is used.  See the
    Django documentation for it's full syntax.

    NOTE: If the live server needs database access to handle a request
          your test will have to request database access.  Furthermore
          when the tests want to see data added by the live-server (or
          the other way around) transactional database access will be
          needed as data inside a transaction is not shared between
          the live server and test code.

          Static assets will be automatically served when
          ``django.contrib.staticfiles`` is available in INSTALLED_APPS.
    """
    skip_if_no_django()

    addr = (request.config.getvalue('liveserver') or os.getenv('DJANGO_LIVE_TEST_SERVER_ADDRESS'))

    if addr and django.VERSION >= (1, 11) and ':' in addr:
        request.config.warn('D001', 'Specifying a live server port is not supported '
                                    'in Django 1.11. This will be an error in a future '
                                    'pytest-django release.')

    if not addr:
        if django.VERSION < (1, 11):
            addr = 'localhost:8081,8100-8200'
        else:
            addr = 'localhost'

    server = LiveServerNgrok(addr=addr, ngrok=ngrok)
    request.addfinalizer(server.stop)
    return server
