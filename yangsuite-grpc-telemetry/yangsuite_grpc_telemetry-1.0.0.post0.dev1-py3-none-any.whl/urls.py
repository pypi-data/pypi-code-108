# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
from django.conf.urls import url
from . import views

app_name = 'grpctelemetry'
urlpatterns = [
    url(r'^$', views.render_main_page, name="main"),
    url(r'^servicer/(?P<port>[0-9]+)/start?$', views.start_servicer,
        name="start_servicer"),
    url(r'^servicer/output', views.get_output,
        name="get_output"),
    url(r'^servicer/(?P<port>[0-9]+)/stop?$', views.stop_servicer,
        name="stop_servicer"),
    url(r'^servicer/list', views.get_servicer_list,
        name="get_servicer_list"),
    url(r'^servicer/config', views.set_output,
        name="set_output"),
]
