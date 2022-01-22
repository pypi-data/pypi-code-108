from django.conf.urls import url
from django.urls import path
from .views import *

app_name = 'chats'

urlpatterns = [
    url(r'^$', ChatSessionListAPIView.as_view(), name='list'),
    url(r'^create/$', ChatSessionCreateAPIView.as_view(), name='create'),
    path('members/<id>/', ChatSessionMemberDetailAPIView.as_view(), name='members-details'),
    path('messages/<id>', ChatSessionMessageDetailAPIView.as_view(), name='messages-details'),
    path('<uri>/members/', ChatSessionMemberListAPIView.as_view(), name='members'),
    path('<uri>/messages/create', ChatSessionMessageCreateAPIView.as_view(), name='messages-create'),
    path('<uri>/messages/', ChatSessionMessageListAPIView.as_view(), name='messages'),
    path('<uri>/mark-as-read/', ChatSessionMarkAsReadAPIView.as_view(), name='mark-as-read'),
    path('<uri>/', ChatSessionDetailAPIView.as_view(), name='details'),
]
