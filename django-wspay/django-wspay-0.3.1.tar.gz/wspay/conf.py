from appconf import AppConf

from django.conf import settings  # noqa


def resolve(setting, **kwargs):
    """Resolve setting to a result of a callable or itself."""
    if hasattr(setting, '__call__'):
        return setting(**kwargs)
    return setting


class WSPayAppConf(AppConf):

    SUCCESS_URL = '/'
    ERROR_URL = '/'
    CANCEL_URL = '/'
    DEVELOPMENT = None
    VERSION = '2.0'
    SHOP_ID = None
    SECRET_KEY = None

    class Meta:
        prefix = 'ws_pay'
        required = ['SHOP_ID', 'SECRET_KEY']

    def configure_development(self, value):
        value = settings.DEBUG if value is None else value
        return self._configure_potentially_callable_setting(value)

    def configure_shop_id(self, value):
        return self._configure_potentially_callable_setting(value)

    def configure_secret_key(self, value):
        return self._configure_potentially_callable_setting(value)

    def configure_success_url(self, value):
        return self._configure_potentially_callable_setting(value)

    def configure_error_url(self, value):
        return self._configure_potentially_callable_setting(value)

    def configure_cancel_url(self, value):
        return self._configure_potentially_callable_setting(value)

    def _configure_potentially_callable_setting(self, value):
        # If redirect_url setting is a callable return it
        if hasattr(value, '__call__'):
            return value

        # Try resolving a setting to a fully qualified name
        # of a function, return the function object if found
        try:
            modname, part_symbol, attr = value.rpartition('.')
            assert part_symbol == '.', value
            assert modname != '', value
        except Exception:
            return value

        try:
            m = __import__(modname, fromlist=[attr])
            f = getattr(m, attr)
            return f
        except Exception:
            raise
