from django.urls import path

from siteconfigs import views

urlpatterns = [
    path("", views.SiteConfigsIndexView.as_view(), name="siteconfigs-index"),
]
