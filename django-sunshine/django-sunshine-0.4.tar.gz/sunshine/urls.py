# -*- coding: utf-8 -*-

# This code is a part of sunshine package: https://github.com/letuananh/sunshine
# :copyright: (c) 2013-2021 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="sunshine_index"),
    path('public/', views.public, name='sunshine_public'),
    path('home/', views.home, name='sunshine_home'),
    path('system/profile/', views.profile, name='sunshine_profile'),
    path('system/dashboard/', views.system_dashboard, name='system_dashboard'),
    path('logout/', views.logout, name='sunshine_logout'),
    # basic-CDN
    path('cdn/', views.cdn_home, name='sunshinecdn'),
    path(r'cdn/avatars/<slug:username>', views.cdn_serve_avatar, name='cdn_avatar'),
    path(r'cdn/direct/<slug:module>/<uuid:res_id>', views.cdn_serve, name='cdn_serve'),
    path(r'cdn/direct/<slug:module>/<uuid:res_id>/<slug:ext>', views.cdn_serve, name='cdn_serve'),
    # common APIs
    path('sunshine/api/common/sidebar',
         views.api_sidebar_toggle, name='ssapi_sidebar_toggle'),
    path('sunshine/api/common/sidebar/<int:status>',
         views.api_sidebar_toggle, name='ssapi_sidebar_toggle'),
    path('sunshine/api/notifications/fetch',
         views.api_fetch_notifications, name='ssapi_notification_fetch')
]
