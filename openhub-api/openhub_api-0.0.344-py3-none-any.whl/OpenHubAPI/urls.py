"""OpenHubAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include
from rest_framework import routers
from django.urls import path
from data.views.views import HardwareViewSet, AccessoryViewSet, CalibrationViewSet, ChannelViewSet, HubViewSet, \
    IOViewSet
#
# # Routers provide an easy way of automatically determining the URL conf.
# router = routers.DefaultRouter()
# router.register(r'accessories', AccessoryViewSet)
# router.register(r'hardwares', HardwareViewSet)
# router.register(r'channel', ChannelViewSet)
# router.register(r'calibration', CalibrationViewSet)
# router.register(r'hubs', HubViewSet)
# router.register(r'io', IOViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include('data.urls')),
    ]
