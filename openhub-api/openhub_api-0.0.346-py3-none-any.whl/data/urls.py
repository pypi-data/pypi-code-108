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
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from django.urls import path
from data.views.views import HardwareViewSet, AccessoryViewSet, CalibrationViewSet, ChannelViewSet, HubViewSet, \
    IOViewSet, createUser,listHubAccessories,listHubHardware,listHubChannels,ChannelStatsViewSet
from django.contrib.auth.views import LoginView


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'accessories', AccessoryViewSet)
router.register(r'hardwares', HardwareViewSet)
router.register(r'channel', ChannelViewSet)
router.register(r'calibration', CalibrationViewSet)
router.register(r'channelstats', ChannelStatsViewSet, basename='channelstats')
router.register(r'hubs', HubViewSet, basename='hubs')
router.register(r'io', IOViewSet)

from data.views.views import index
from data.views.views import video_streams, logout

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    url(r'^login/$', LoginView.as_view(template_name="registration/login.html"), name="login"),
    url(r'^logout/$', logout, name="logout"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('start', views.start, name='start'),
    # path('calibrate', views.start, name='calibrate'),
    path('index', index, name='index'),
    url(r'^admin/', admin.site.urls),
    path('post/ajax/hardware', HardwareViewSet.postHardware, name="post_hardware"),
    path('post/ajax/hardware/form_type/', HardwareViewSet.getHardwareTypeForm,
         name="get_hardware_types"),
    path('post/ajax/hardware/form_io/', HardwareViewSet.getHardwareIoForm,
         name="get_hardware_io"),
    path('post/ajax/accessory', AccessoryViewSet.postAccessory, name="post_accessory"),
    path('delete/ajax/accessory', AccessoryViewSet.deleteAccessory, name="delete_accessory"),
    path('post/ajax/calibration', AccessoryViewSet.postCalibration, name="post_calibration"),
    path('patch/ajax/accessory', AccessoryViewSet.updateAccessory, name="update_accessory"),
    path('delete/ajax/hub', HubViewSet.deleteHub, name="delete_hub"),
    path('patch/ajax/hub', HubViewSet.updateHub, name="update_hub"),

    path('patch/ajax/calibration', CalibrationViewSet.updateCalibration, name="update_calibration"),
    path('delete/ajax/channel', ChannelViewSet.deleteChannel, name="delete_channel"),
    path('delete/ajax/hardware', HardwareViewSet.deleteHardware, name="delete_hardware"),
    path('delete/ajax/io', IOViewSet.deleteIO, name="delete_io"),

    path('post/ajax/hardware/io/', HardwareViewSet.postHardwareIO,
         name="post_hardware_io"),
    path('post/ajax/calibrationconstant', CalibrationViewSet.postCalibrationConstant, name="post_calibration_constant"),
    path('post/ajax/channel', HardwareViewSet.postChannel, name="post_channel"),
    path('patch/ajax/channel', ChannelViewSet.updateChannel, name="update_channel"),
    path('post/ajax/config', HardwareViewSet.postConfig, name="post_config"),
    path('patch/ajax/hardware', HardwareViewSet.updateHardware, name="update_hardware"),
    path('hardwares/<uuid:hardware_id>/config', HardwareViewSet.getConfig),
    path('hardwares/<uuid:hardware_id>/channels', HardwareViewSet.getChannels),
    path('channels/<uuid:channel_id>/io', ChannelViewSet.listIO),
    path('accessories/<uuid:accessory_id>/data_transformer', AccessoryViewSet.postDataTransformer),

    # path('<str:room_name>/', views.room, name='room'),
    path('post/ajax/hub', HubViewSet.postHub, name="post_hub"),
    path('hub/', csrf_exempt(HubViewSet.postHub)),
    path('pipico/', csrf_exempt(HardwareViewSet.postHardware)),

    path('hubs/<uuid:hub_id>/hardwares', view=listHubHardware),
    path('hubs/<uuid:hub_id>/channels', view=listHubChannels),
    path('hubs/<uuid:hub_id>/accessories', view=listHubAccessories),
    path('openhubapi/about', HubViewSet.about),
    path('streams/', video_streams, name="video_streams"),
    # url('createuser', createUser, name='create_user'),
    path('createuser/', createUser, name="create_user"),

]
