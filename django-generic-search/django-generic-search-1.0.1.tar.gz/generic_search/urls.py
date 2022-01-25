from django.urls import path

from . import views

app_name = 'generic_search'
urlpatterns = [
    path('', views.GeneralSearch.as_view(), name='generic_search'),
]
