from django.conf.urls import url, include

from .views import AuditSortAdminAPIView, AuditAdminListAPIView

app_name = 'audits'

urlpatterns = [
    url(r'^$', AuditAdminListAPIView.as_view(), name='list'),
    url(r'^sort/$', AuditSortAdminAPIView.as_view(), name='sort'),
]
