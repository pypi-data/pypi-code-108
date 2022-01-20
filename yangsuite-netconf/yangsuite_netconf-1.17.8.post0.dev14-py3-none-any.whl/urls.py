# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
from django.conf.urls import url
from . import views

app_name = 'netconf'
urlpatterns = [
    url(r'^$', views.get_yang, name='getyangbak'),
    url(r'^getyang/(?:(?P<yangset>[^/]+)/?(?P<modulenames>[^/]+)?)?',
        views.get_yang, name='getyang'),
    url(r'^getrpc/', views.get_rpc, name='getrpc'),
    url(r'^gettaskrpc/', views.get_task_rpc, name='gettaskrpc'),
    url(r'^runrpc/', views.run_rpc, name='runrpc'),
    url(r'^runresult/[^/]*$', views.run_result, name='runresult'),
    url(r'^clearrpc/', views.clear_rpc_results, name='clearrpc'),
    url(r'^schemas/list/', views.list_schemas, name="listschemas"),
    url(r'^schemas/download/', views.download_schemas, name="downloadschemas"),
    url(r'^lock/set', views.lock_unlock_datastore,
        name='lockunlockdatastore'),
    url(r'^session/start_end', views.start_end_session,
        name='startendsession'),
    url(r'^capabilities/', views.list_capabilities, name='capabilities'),
    url(r'^datastores/', views.list_datastores, name='datastores'),
    url(r'^setlog/', views.set_log, name='setlog'),
]
