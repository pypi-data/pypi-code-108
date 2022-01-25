"""General urls for ecommerce-extensions."""
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from ecommerce_extensions.payment import urls

urlpatterns = [
    path("payu/", include((urls.PAYU_URLS, "ecommerce_extensions"), namespace="payu")),
    path("wechat/", include((urls.FOMOPAY_URLS, "ecommerce_extensions"), namespace='fomopay')),
    path("edupay/", include((urls.EDUPAY_URLS, "ecommerce_extensions"), namespace="edupay")),
]

if getattr(settings, 'TESTING', False):
    urlpatterns += [
        path('', include(apps.get_app_config('oscar').urls[0])),
        path('i18n/', include('django.conf.urls.i18n')),
        path('admin/', admin.site.urls),
    ]
