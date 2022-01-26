from django.conf.urls import url
from .views import JobOffersCurrentViewset, \
                   JobOffersExpiredViewset, JobOfferServerNotificationView
from .models import JobOffer

urlpatterns = [
    url(r'^job-offers/current/', JobOffersCurrentViewset.urls(model_prefix="joboffer-current", model=JobOffer)),
    url(r'^job-offers/expired/', JobOffersExpiredViewset.urls(model_prefix="joboffer-expired", model=JobOffer)),
    url(r'^job-offers/inbox/', JobOfferServerNotificationView.as_view(), name="joboffer-notify-all"),
]
