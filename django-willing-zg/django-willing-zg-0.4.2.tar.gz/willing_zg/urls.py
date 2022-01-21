from django.urls import path

from . import views

app_name = "zygoat"


urlpatterns = [
    path("env/", views.get_frontend_env, name="get_frontend_env"),
    path("health/", views.health, name="health"),
]
