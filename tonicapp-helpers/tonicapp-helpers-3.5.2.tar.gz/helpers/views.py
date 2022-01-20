from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.http import HttpResponse
from django.views import View


class BaseMonitoringView(View):
    tests = []

    def get(self, request):
        failed = []

        for test in self.tests:
            if not test.check():
                failed.append(test.response)

        if len(failed) > 0:
            return HttpResponse(failed, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return HttpResponse('OK', status.HTTP_200_OK)


class BaseMonitoringViewSet(viewsets.GenericViewSet):
    ping_tests = []
    pong_tests = []

    @action(
        detail=False,
        methods=['get'],
        url_path=''
    )
    def ping(self, request):
        failed = []

        for test in self.ping_tests:
            if not test.check():
                failed.append(test.response)

        if len(failed) > 0:
            return Response(
                failed,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response('OK', status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        url_path=''
    )
    def pong(self, request):
        failed = []

        for test in self.pong_tests:
            if not test.check():
                failed.append(test.response)

        if len(failed) > 0:
            return Response(
                failed,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response('OK', status=status.HTTP_200_OK)
