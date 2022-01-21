from django.urls import path

from ingress.views import IngressView

urlpatterns = [
    path("<collection_name>/", IngressView.as_view(), name="ingress"),
]
