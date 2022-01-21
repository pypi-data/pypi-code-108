import logging

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ingress.models import Collection, Message
from ingress.settings import app_settings

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class IngressView(APIView):
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in app_settings.PERMISSION_CLASSES]

    def get_authenticators(self):
        """
        Instantiates and returns the list of authenticators that this view can use.
        """
        return [auth() for auth in app_settings.AUTHENTICATION_CLASSES]

    def post(self, request, collection_name):
        # check if the collection exists and is active
        collection = get_object_or_404(Collection, name=collection_name)
        if not collection.ingress_enabled:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data="Ingress for collection is disabled",
            )

        raw_data = request.body.decode(app_settings.ENCODING)
        try:
            Message.objects.create(collection=collection, raw_data=raw_data)
            return Response(status=status.HTTP_200_OK)
        except Exception:
            logger.exception("Failed to create Message")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
