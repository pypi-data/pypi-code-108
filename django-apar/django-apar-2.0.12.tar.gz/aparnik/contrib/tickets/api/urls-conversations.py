from django.conf.urls import url, include

from .views import TicketConversationListAPIView, TicketConversationCreateAPIView

app_name = 'tickets'

urlpatterns = [
    url(r'^$', TicketConversationListAPIView.as_view(), name='list'),
    url(r'^create/$', TicketConversationCreateAPIView.as_view(), name='create'),

]