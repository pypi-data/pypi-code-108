"""data_middle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework.renderers import OpenAPIRenderer
from rest_framework.routers import SimpleRouter
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer


from .direct.views import TlmsWmsEntDirectListViewSet
from .tlms_wms_public_table.views import CargoListViewSet, ConsignorViewSet, DecMethodViewSet, \
    WorkRouteViewSet, TransModeViewSet, CurrencyViewSet, TransportModeViewSet, CustomsModeViewSet, \
    DomesticDestinationViewSet, \
    CtnSizeViewSet, CtnTypeViewSet, SupplierViewSet, UnPackTypeListViewSet, ForkliftViewSet, CountryViewSet, \
    MeasureViewSet, TradeModeViewSet

schema_view = get_schema_view(title='TLMS API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])


class OptionalSlashRouter(SimpleRouter):

    def __init__(self):
        self.trailing_slash = '/?'
        super(SimpleRouter, self).__init__()


router = OptionalSlashRouter()

router.register(r'cargo', CargoListViewSet, basename="cargo")
router.register(r'consignor', ConsignorViewSet, basename="consignor")
router.register(r'dec-method', DecMethodViewSet, basename="dec-method")
router.register(r'work-route', WorkRouteViewSet, basename="work-route")
router.register(r'ctn-size', CtnSizeViewSet, basename="ctn-size")
router.register(r'ctn-type', CtnTypeViewSet, basename="ctn-type")
router.register(r'supplier', SupplierViewSet, basename="supplier")
router.register(r'unpack-mode', UnPackTypeListViewSet, basename="unpack-mode")
router.register(r'forklift', ForkliftViewSet, basename="forklift")
# 一体化平台映射基础代码表
router.register(r'trans_mode', TransModeViewSet, basename="trans_mode")
router.register(r'currency', CurrencyViewSet, basename="currency")
router.register(r'transport_mode', TransportModeViewSet, basename="transport_mode")
router.register(r'customs_mode', CustomsModeViewSet, basename="customs_mode")
router.register(r'domestic_destination', DomesticDestinationViewSet, basename="domestic_destination")
router.register(r'country', CountryViewSet, basename="country")
router.register(r'measure', MeasureViewSet, basename="measure")
router.register(r'trade_mode', TradeModeViewSet, basename="trade_mode")


router.register(r'wms-direct', TlmsWmsEntDirectListViewSet, basename="wms-direct")




urlpatterns = [
    # url(r'docs/', include_docs_urls(title="中台数据")),
    # url('docs_schema/', schema_view, name="中台数据"),
    url(r'^', include(router.urls)),
]
