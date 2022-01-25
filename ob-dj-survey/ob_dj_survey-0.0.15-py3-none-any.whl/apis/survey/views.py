import logging

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, viewsets

from ob_dj_survey.apis.survey.permissions import SurveyManagerPermission
from ob_dj_survey.apis.survey.serializers import (
    SurveyAnswerSerializer,
    SurveySerializer,
)
from ob_dj_survey.core.survey.models import Survey, SurveyAnswer

logger = logging.getLogger(__name__)


@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Create Survey",
        operation_description="""
        Write a Description
        """,
        tags=["Survey",],
    ),
)
@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="List Survey",
        operation_description="""
        Write a Description
        """,
        tags=["Survey",],
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Retrieve Survey",
        operation_description="""
        Write a Description
        """,
        tags=["Survey",],
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Delete Survey",
        operation_description="""
        Write a Description
        """,
        tags=["Survey",],
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Update Survey",
        operation_description="""
        Write a Description
        """,
        tags=["Survey",],
    ),
)
@method_decorator(
    name="update", decorator=swagger_auto_schema(auto_schema=None),
)
class SurveyView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, SurveyManagerPermission]
    serializer_class = SurveySerializer
    queryset = Survey.objects.active()


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Survey Answer",
        operation_description="""
        Write a Description
        """,
        tags=["Survey",],
    ),
)
class SurveyAnswerView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SurveyAnswerSerializer
    queryset = SurveyAnswer.objects.all()
