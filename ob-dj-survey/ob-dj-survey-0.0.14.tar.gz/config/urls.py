from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path

urlpatterns = [
    re_path(r"^$", lambda request: HttpResponse("Alive !"), name="ping",),
    path("admin/", admin.site.urls),
    path("survey/", include("ob_dj_survey.apis.survey.urls", namespace="survey"),),
]
urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
]
