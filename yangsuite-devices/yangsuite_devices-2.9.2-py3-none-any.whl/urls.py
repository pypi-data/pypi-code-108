# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
from django.conf.urls import url
from . import views


app_name = 'devices'
urlpatterns = [
    # Get the main web page used to manage device profiles
    url(r'^(?:devprofile)?/?$', views.devices_page, name='devices_page'),
    # Get the list of devices
    url(r'^list/', views.list_devices, name='list_devices'),
    # Get the forms the user needs for creating or editing a device
    url(r'^new/?', views.new_device_form, name='new_device_form'),
    url(r'^clone/(?P<device_key>[^/]+)/?', views.edit_device_form,
        name='clone_device_form'),
    url(r'^edit/(?P<device_key>[^/]+)/?', views.edit_device_form,
        name='edit_device_form'),
    # Check validity and connectivity of a candidate (or existing) device
    url(r'^check/?$', views.check_device, name='check_device'),
    url(r'^check/(?P<device_key>[^/]+)/?',
        views.check_device, name="check_device"),
    # Create, read, update, or delete a given device profile
    url(r'^device/?$', views.device_crud, name='device_crud'),
    url(r'^device/(?P<device_key>[^/]+)/?',
        views.device_crud, name='device_crud'),
    url(r'^device-defaults/(?P<device_key>[^/]+)/?',
        views.create_default_repo_yangset,
        name='create_default_repo_yangset'),
    url(r'^upload/(?P<device_key>[^/]+)/?',
        views.file_upload, name='device_file'),
]
