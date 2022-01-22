from django.conf.urls import url

from .views import payment, callback_view

app_name = 'payments'

urlpatterns = [
    url(r'^(?P<uuid>[0-9a-f-]+)/pay/$', payment, name='payment'),
    url(r'^verify/$', callback_view, name='call-back'),
    # url(r'^(?P<id>\d+)/pay/$', TransactionPayAPIView.as_view(), name='pay'),
    # url(r'^(?P<id>\d+)/$', TransactionDetailAPIView.as_view(), name='detail'),

]
