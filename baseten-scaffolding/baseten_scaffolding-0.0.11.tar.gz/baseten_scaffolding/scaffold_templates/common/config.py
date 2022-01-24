import os
from common.lib_support import ensure_sentry_sdk_installed

def do_sentry_init():
    SENTRY_URL = os.environ.get('SENTRY_URL', '')
    RUNTIME_ENV = os.environ.get('RUNTIME_ENV', '')
    if SENTRY_URL is not '':
        ensure_sentry_sdk_installed()
        import sentry_sdk
        from sentry_sdk import set_tag
        from sentry_sdk.integrations.tornado import TornadoIntegration
        sentry_sdk.init(
            dsn=SENTRY_URL,
            integrations=[TornadoIntegration()],
            environment=RUNTIME_ENV,

        )
        set_tag('environment', RUNTIME_ENV)
