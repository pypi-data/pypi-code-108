# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
from django.conf.urls import url
from . import views

app_name = 'yscoverage'
urlpatterns = [
    url(r'^coverage/', views.render_main_page, name="main"),
    url(r'^getconfig/', views.getconfig, name="getconfig"),
    url(r'^getreleases/', views.getreleases, name="getreleases"),
    url(r'^getcoverage/', views.getcoverage, name='getcoverage'),
    url(r'^datasets/', views.render_datasets_page, name='datasets'),
    url(r'^getdataset/', views.get_dataset, name='getdataset'),
    url(r'^getdiff/', views.get_diff, name='getdiff'),
]
