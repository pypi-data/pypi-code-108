from django.conf.urls import url, include

from .views import TicketListAPIView, TicketCreateAPIView#, CourseDetailAPIView, CourseUserListAPIView, CourseCreateAPIView

app_name = 'tickets'

urlpatterns = [
    url(r'^$', TicketListAPIView.as_view(), name='list'),
    url(r'^(?P<ticket_id>\d+)/conversations/', include('aparnik.contrib.tickets.api.urls-conversations', namespace='conversations')),
    url(r'^create/$', TicketCreateAPIView.as_view(), name='create'),
    url(r'^admin/', include('aparnik.contrib.tickets.api.admin.urls', namespace='admin')),


]