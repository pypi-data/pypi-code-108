from django.urls import path

from autoreduce_rest_api.runs import views

app_name = "runs"

urlpatterns = [
    path('runs/<str:instrument>', views.ManageRuns.as_view(), name="manage"),
    path('runs/batch/<str:instrument>', views.BatchSubmit.as_view(), name="batch"),
]
