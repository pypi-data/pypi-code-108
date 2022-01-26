from django.urls.conf import path
from django.views.generic import RedirectView

app_name = "mocca_export"

urlpatterns = [
    path("", RedirectView.as_view(url="/mocca_export/admin/"), name="home_url"),
]
