from django.urls.conf import path
from django.views.generic import RedirectView

app_name = "mocca_ae"

urlpatterns = [
    path("", RedirectView.as_view(url="/mocca_ae/admin/"), name="home_url"),
]
