import askbot
from haystack.routers import BaseRouter
from haystack.constants import DEFAULT_ALIAS

from .utils import alias_from_language, get_language

def get_alias():
    if askbot.is_multilingual():
        language = get_language()
        return alias_from_language(language)
    return DEFAULT_ALIAS


class LanguageRouter(BaseRouter):

    def for_read(self, **hints):
        return get_alias()

    def for_write(self, **hints):
        return get_alias()
