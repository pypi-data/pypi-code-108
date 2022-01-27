import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


def get_language_from_request(request):
    """Custom version of django get_language_from_request from translation.

    Remove path and cookies parsing and just use X-Custom-language as
    first choice if it is defined and valid, then use Accept-Language.
    """
    _trans = translation._trans  # Load _trans dynamically from translation.

    custom_lang = translation.to_language(
        request.META.get('HTTP_X_CUSTOM_LANGUAGE', ''))
    try:
        return _trans.get_supported_language_variant(custom_lang)
    except LookupError:
        pass

    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    for accept_lang, unused in _trans.parse_accept_lang_header(accept):
        if accept_lang == '*':
            break  # pragma: no cover
        if not _trans.language_code_re.search(accept_lang):
            continue  # pragma: no cover
        try:
            return _trans.get_supported_language_variant(accept_lang)
        except LookupError:
            continue

    try:
        return _trans.get_supported_language_variant(settings.LANGUAGE_CODE)
    except LookupError:  # pragma: no cover
        return settings.LANGUAGE_CODE


class LocaleMiddleware(MiddlewareMixin):
    response_redirect_class = HttpResponseRedirect

    def process_request(self, request):
        language = get_language_from_request(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        code = (
            len(request.LANGUAGE_CODE) == 5 and
            request.LANGUAGE_CODE[:3] + request.LANGUAGE_CODE[-2:].upper() or
            request.LANGUAGE_CODE)
        response.headers.setdefault('Content-Language', code)
        return response
