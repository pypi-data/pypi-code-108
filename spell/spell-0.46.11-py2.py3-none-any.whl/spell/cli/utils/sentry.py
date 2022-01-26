import os
import sys
import traceback

import sentry_sdk
from sentry_sdk.integrations.argv import ArgvIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.scope import add_global_event_processor

from spell import version, deployment_constants
from spell.cli.log import logger_name


SENTRY_URL = "https://9a9530b86ed74e11a28e7f410f31bab7@sentry.io/1285204"
ENVIRONMENT_SUPPRESS_VALUE = "SPELL_QUIET"


_inited = False
_tags = {}
_user = None


class PasswordStrippedArgvIntegration(ArgvIntegration):
    # This class has been copied from
    # https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/integrations/argv.py
    # And modified to strip out password
    identifier = "argv"

    @staticmethod
    def setup_once():
        @add_global_event_processor
        def processor(event, _hint):
            extra = event.setdefault("extra", {})
            # If some event processor decided to set extra to e.g. an
            # `int`, don't crash. Not here.
            if isinstance(extra, dict):
                processed_args = []
                is_next_password = False
                for arg in sys.argv:
                    if is_next_password:
                        is_next_password = False
                        arg = "REDACTED"
                    elif arg == "--password":
                        is_next_password = True
                    processed_args.append(arg)

                extra["sys.argv"] = processed_args

            return event


def _init_sentry():
    global _inited
    if _inited:
        return

    sentry_sdk.init(
        SENTRY_URL,
        release=version.__version__,
        integrations=[
            DedupeIntegration(),
            StdlibIntegration(),
            ModulesIntegration(),
            PasswordStrippedArgvIntegration(),
        ],
        default_integrations=False,
    )

    ignore_logger(logger_name)

    _inited = True


def _configure_scope():
    if not _inited:
        return

    with sentry_sdk.configure_scope() as scope:
        scope.clear()
        scope.user = _user
        for k, v in _tags.items():
            scope.set_tag(k, v)


def set_user(user):
    global _user
    _user = user


def set_tag(key, value):
    global _tags
    _tags[key] = value


def capture_exception(error):
    if deployment_constants.on_prem:
        print("Contact Spell if this issue continues: {}".format(error))
    elif ENVIRONMENT_SUPPRESS_VALUE not in os.environ:
        _init_sentry()
        _configure_scope()
        sentry_sdk.capture_exception(error)
    else:
        traceback.print_exc()


def capture_message(message, level=None):
    if deployment_constants.on_prem:
        print("Contact Spell if this issue continues: {}".format(message))
    elif ENVIRONMENT_SUPPRESS_VALUE not in os.environ:
        _init_sentry()
        _configure_scope()
        sentry_sdk.capture_message(message, level)
    else:
        print("Message intended for sentry: {}".format(message))
