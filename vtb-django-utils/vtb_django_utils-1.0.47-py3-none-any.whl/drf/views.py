from rest_framework.response import Response
from rest_framework.views import APIView


class StatusCheckView(APIView):
    """ REST API проверки статуса """

    @staticmethod
    def get(request):  # pylint: disable=unused-argument
        """ GET """
        return Response({
            'status': 'ok',
        })
