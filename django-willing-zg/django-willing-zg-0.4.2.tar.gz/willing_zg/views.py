from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(["GET"])
def get_frontend_env(request):
    return Response(getattr(settings, "ZYGOAT_FRONTEND_META_CONFIG", {}))


@api_view(["GET"])
def health(request):
    return Response({})
