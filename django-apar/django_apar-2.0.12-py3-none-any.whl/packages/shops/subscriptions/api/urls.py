from django.conf.urls import url, include

from .views import SubscriptionListAPIView, SubscriptionOrderListAPIView, SubscriptionOrderActiveListAPIView

app_name = 'subscriptions'

urlpatterns = [
    url(r'^$', SubscriptionListAPIView.as_view(), name='list'),
    url(r'^mine-history/$', SubscriptionOrderListAPIView.as_view(), name='list-mine'),
    url(r'^mine-active/$', SubscriptionOrderActiveListAPIView.as_view(), name='list-active'),
]
