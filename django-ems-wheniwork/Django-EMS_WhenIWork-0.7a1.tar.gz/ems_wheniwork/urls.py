from django.conf.urls import url

from .views import serviceorders
from .views.api.schedule import Schedule
from .views.api.shift import Shift

urlpatterns = [
    url(r'^$', serviceorders.index, name='ems_wheniwork'),

    url(r'^api/v1/shift/(?P<shift_id>\d+)?$', Shift().run),
    url(r'^api/v1/schedule/$', Schedule().run),
]
