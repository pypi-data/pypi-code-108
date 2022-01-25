from rest_framework.decorators import api_view
from rest_framework.response import Response
from rygg import settings
from rygg import __version__
from rygg.api.app import updates_available

@api_view(['GET'])
def get_version(request):
    return Response({"version": __version__})


@api_view(['GET'])
def get_updates_available(request):
    return Response({"newer_versions": updates_available()})

@api_view(["GET"])
def is_enterprise(request):
    return Response({"is_enterprise": settings.IS_CONTAINERIZED})
