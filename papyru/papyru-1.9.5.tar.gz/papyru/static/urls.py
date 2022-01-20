from django.urls import re_path

from . import views

urlpatterns = [
    re_path('^/(.+)$', views.StaticFilesList(), name='papyru_static_files'),
]
