from common_structure_microservices.messages import Messages
from common_structure_microservices.profiles import Profiles
from common_structure_microservices.utilities import Constants
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param


class CustomPagination(LimitOffsetPagination):
    config_profile = Profiles()
    URL_SERVER = 'https://studentsprojects.cloud.ufps.edu.co/asn_balancing/api_gateway/'

    def get_paginated_response(self, data):
        return Response({
            'paginator': {
                'count': self.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'status': True,
            'message': Messages.SUCCESSFUL_MESSAGE,
            'data': data
        })

    def get_next_link(self):
        if self.config_profile.PROFILE == Constants.DEVELOP:
            if self.offset + self.limit >= self.count:
                return None

            url_base = self.request.build_absolute_uri()
            url = self.replace_url_develop(url_base)
            url = replace_query_param(url, self.limit_query_param, self.limit)

            offset = self.offset + self.limit
            return replace_query_param(url, self.offset_query_param, offset)
        else:
            return super().get_next_link()

    def get_previous_link(self):
        if self.config_profile.PROFILE == Constants.DEVELOP:
            if self.offset <= 0:
                return None

            url_base = self.request.build_absolute_uri()
            url = self.replace_url_develop(url_base)
            url = replace_query_param(url, self.limit_query_param, self.limit)

            if self.offset - self.limit <= 0:
                return remove_query_param(url, self.offset_query_param)

            offset = self.offset - self.limit
            return replace_query_param(url, self.offset_query_param, offset)
        else:
            return super().get_previous_link()

    def replace_url_develop(self, url_with_ip):
        app_name = self.config_profile.APP_NAME
        rest_url = url_with_ip[url_with_ip.find(self.config_profile.APPLICATION['context_path']):]
        return f'{self.URL_SERVER}{app_name}/{rest_url}'
