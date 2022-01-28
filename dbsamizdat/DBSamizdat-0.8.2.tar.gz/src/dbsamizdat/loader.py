from logging import getLogger
from importlib import import_module
import inspect
from itertools import chain

from .samizdat import SamizdatView, SamizdatMaterializedView, SamizdatFunction, SamizdatTrigger, SamizdatMeta, SamizdatFunctionMeta, SamizdatTriggerMeta


logger = getLogger(__name__)

AUTOLOAD_MODULENAME = "dbsamizdat_defs"


def get_samizdats(modulelist=None, only_that_modulelist=False):

    def issamizdat(thing):
        excluded_classes = {SamizdatView, SamizdatMaterializedView, SamizdatFunction, SamizdatTrigger}
        return inspect.isclass(thing) and isinstance(thing, (SamizdatMeta, SamizdatFunctionMeta, SamizdatTriggerMeta)) and (thing not in excluded_classes)

    sdmodules = [import_module(sdmod) for sdmod in (modulelist or [])]
    if not only_that_modulelist:
        try:
            # if we're running in Django, we can try to autoload things
            from django.core.exceptions import ImproperlyConfigured
            from django.conf import settings
            from django.apps import apps
        except ImportError:
            pass  # no Django
        else:
            try:
                django_sdmodules = [import_module(sdmod) for sdmod in getattr(settings, 'DBSAMIZDAT_MODULES', [])]
                for appconfig in apps.get_app_configs():
                    try:
                        django_sdmodules.append(import_module('{}.{}'.format(appconfig.module.__package__, AUTOLOAD_MODULENAME)))
                    except ImportError as err:
                        if not err.msg.endswith(f"{AUTOLOAD_MODULENAME}'"):
                            raise err
                if not django_sdmodules:
                    logger.warn("""No settings.DBSAMIZDAT_MODULES defined, and none of your apps contain any "dbsamizdat_defs" module to autoload.""")
                sdmodules += django_sdmodules
            except ImproperlyConfigured:
                # assume we're not running in a fully booted Django
                pass

    return set((c for cname, c in chain(*map(lambda m: inspect.getmembers(m, issamizdat), sdmodules))))
