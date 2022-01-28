#-*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

import mediautils
from mediautils.views import del_photo


urlpatterns = [
    url(r'^del-photo/(?P<pk>\d+)/$', mediautils.views.del_photo, name='del_photo'),
    ]
