from django.conf.urls import url
from . import views

app_name = 'gnmi'
urlpatterns = [
    url(r'^$', views.render_main_page, name="main"),
    url(r'^explore/(?:(?P<yangset>[^/]+)/?(?P<modulenames>[^/]+)?)?',
        views.render_main_page, name="explore"),
    url(r'^tree/?', views.get_json_tree, name='get_json_tree'),
    url(r'^build_get/?$', views.build_get_request, name='build_get_request'),
    url(r'^build_set/?$', views.build_set_request, name='build_set_request'),
    url(r'^showreplay/?$', views.show_replay, name='showreplay'),
    url(r'^run/(?P<device>.*)$', views.run_request, name="run_request"),
    url(r'^runresult/(?P<device>.*)$', views.run_result, name='runresult'),
    url(r'^runreplay/(?P<device>.*)$', views.run_replay, name="run_replay"),
    url(
        r'^stop/session/(?P<device>.*)$',
        views.stop_session,
        name="stop_session"
    ),
]
