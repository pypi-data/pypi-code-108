import os

import publisher.settings as settings
from publisher.exceptions import InvalidLocaleError


def get_and_check_locale_directory(locale):
    locale_directory = get_locale_directory(locale)

    if not os.path.exists(locale_directory):
        os.makedirs(locale_directory)

    return locale_directory


def get_locale_directory(locale):

    if locale not in settings.LOCALE_DIRECTORIES:
        raise InvalidLocaleError(locale)

    return os.path.join(settings.TRANSLATIONS_CHECKOUT_DIRECTORY,
                        settings.LOCALE_DIRECTORIES[locale], 'LC_MESSAGES')
