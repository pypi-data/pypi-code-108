import logging

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from history import utils
from history.models.history import History
from isc_common.http.DSResponse import Body
from isc_common.json import BytesToJson, StrToJson

logger = logging.getLogger(__name__)


class LoggingRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):

        if request.content_type not in ['text/xml', 'application/json']:
            return

        self.json = BytesToJson(request.body)

        if settings.INCLUDE_REQUEST_PATHES is None:
            settings.INCLUDE_REQUEST_PATHES = set('Add', 'Update', 'Remove')

        if isinstance(settings.INCLUDE_REQUEST_PATHES, list):
            settings.INCLUDE_REQUEST_PATHES = set(settings.INCLUDE_REQUEST_PATHES)

        if settings.DEBUG:
            for param in ['Get', 'Fetch']:
                settings.INCLUDE_REQUEST_PATHES.add(param)

        if request.path != '/':
            user = Body(request.body, request.session).user
            if user:
                username = user.username
                fio = user.get_short_name
                if username is not None:
                    path = set(request.path.split('/'))
                    enable_logging = len(path.intersection(settings.INCLUDE_REQUEST_PATHES)) > 0
                    if enable_logging and len(self.json) > 0:
                        ip_address = utils.get_ip(request)
                        user_agent = request.META.get('HTTP_USER_AGENT')

                        history_element = History.objects.using('history').create(
                            username=username,
                            fio=fio,
                            method=request.method,
                            ip_address=ip_address,
                            user_agent=user_agent,
                            path=request.path,
                            data=self.json
                        )

                        # history_element.ip_address=ip()

                        logger.debug('=========================================================================================================')
                        logger.debug(f'date: {history_element.date}')
                        logger.debug(f'username: {username}')
                        logger.debug(f'method: {request.method}')
                        logger.debug(f'path: {request.path}')
                        logger.debug(f'ip_address: {ip_address}')
                        logger.debug(f'user_agent: {user_agent}')
                        logger.debug(f'json: {StrToJson(self.json)}')
                        logger.debug('=========================================================================================================\n')

    def process_response(self, request, response):
        return response
