import re
import requests
import logging

from ast import literal_eval

from django.conf import settings

logger = logging.getLogger()


class LanguageMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_string = str(response.content, encoding='UTF-8')
        keys = re.findall(r'(\*\*.*?\*\*)', content_string)

        if len(keys) == 0:
            return response

        locale = request.locale

        params = {
            'language_code': locale,
            'features': settings.LANGUAGE["FEATURES"],
            'keys': ",".join(keys)
        }
        headers = {
            'Accept-Language': locale,
            'Authorization': f'TWT {settings.AUTHENTICATION["TONIC_WEB_TOKEN"]}'
        }
        language_response = requests.get(
            settings.LANGUAGE["URL"],
            params=params,
            headers=headers
        )

        if language_response.status_code != 200:
            logger.error(f'Error getting the translations for this response, code: {language_response.status_code}, response: {str(language_response.content)}')
            return response

        language_response_string = str(language_response.content, encoding='UTF-8')
        if '"count":0' in language_response_string:
            logger.warning(f'No keys were found in language service with this params: {params}.')
            return response

        dict_response = language_response_string.split('"results":')[1]
        dict_response = dict_response.replace('null', 'None')
        dict_response = literal_eval(dict_response[:-1])
        for result in dict_response:
            content_string = content_string.replace(result['key'], result['value'])

        response.content = content_string
        return response
