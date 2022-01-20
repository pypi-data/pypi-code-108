import logging

from re import fullmatch

from django.utils.translation import activate
from django.http import HttpResponseBadRequest
from django.conf import settings

logger = logging.getLogger()


class LocaleMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.debug(request.headers)

        if not any(path in request.path for path in settings.EXCLUDE_PATHS):
            accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE')

            if not accept_language:
                return HttpResponseBadRequest(
                    'Add Accept-Language to the header. Example: '
                    + 'Accept-Language: pt-PT'
                )

            accept_language = accept_language.split(',')[0] if ',' \
                in accept_language else accept_language
            accept_language = accept_language.split(';')[0] if ';' \
                in accept_language else accept_language

            if not fullmatch('^[a-z]{2}-[A-Z]{2}$', accept_language):
                return HttpResponseBadRequest(
                    'Incorrect Accept-Language. Example: '
                    + 'Accept-Language: pt-PT'
                )

            # V2.13.6: Temporary fix
            if accept_language not in ['el-GR', 'en-GB', 'de-DE', 'it-IT',
                                       'fr-FR', 'es-ES', 'pt-PT']:
                logger.warning('This accept language does not exist. ' +
                               f'Accept Language: {accept_language};')
                accept_language = 'pt-PT'
            # End of logic

            activate(accept_language)

            request.locale = accept_language

        response = self.get_response(request)

        return response
