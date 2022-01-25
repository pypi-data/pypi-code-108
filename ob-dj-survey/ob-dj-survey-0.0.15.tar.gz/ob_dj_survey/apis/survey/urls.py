from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from ob_dj_survey.apis.survey.views import SurveyAnswerView, SurveyView

app_name = "survey"

router = DefaultRouter()

router.register(r"", SurveyView, basename="survey")

urlpatterns = [
    path("", include(router.urls)),
    path("answers", SurveyAnswerView.as_view(), name="survey-answers"),
]
