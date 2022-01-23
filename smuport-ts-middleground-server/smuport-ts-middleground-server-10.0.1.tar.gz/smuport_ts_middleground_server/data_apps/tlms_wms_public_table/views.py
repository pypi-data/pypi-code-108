# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend

from ..utils.page import CargoPageSetPagination, YzPageSetPagination
from ..utils.yzModelViewSet import FalseDeleteModelViewSet, IntegratedPlatformFalseDeleteModelViewSet
from . import models
from . import serializer
from rest_framework import filters


class SupplierViewSet(FalseDeleteModelViewSet):
    """
    供应商
    """
    def get_queryset(self):
        return models.Supplier.objects.all().filter(if_deleted=False, service_provider=self.request.user.company.id)
    pagination_class = YzPageSetPagination
    serializer_class = serializer.SupplierSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ["name", "code"]
    ordering_fields = ["name"]


class CargoListViewSet(FalseDeleteModelViewSet):
    """
    货物
    """
    def get_queryset(self):
        return models.Cargo.objects.all().filter(if_deleted=False, service_provider=self.request.user.company.id)
    serializer_class = serializer.CargoSerializer
    pagination_class = CargoPageSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['name', 'id', 'code', 'hs_code']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用
    ordering_fields = ['name','id', 'code', 'hs_code']


class ConsignorViewSet(FalseDeleteModelViewSet):
    """
    委托公司
    """
    def get_queryset(self):
        return models.Consignor.objects.all().filter(if_deleted=False, service_provider=self.request.user.company.id)
    serializer_class = serializer.ConsignorSerializer
    pagination_class = YzPageSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['name', 'code', 'register_no']


class DecMethodViewSet(FalseDeleteModelViewSet):
    """
    申报方式
    """
    def get_queryset(self):
        return models.DecMethod.objects.all().filter(if_deleted=False, service_provider=self.request.user.company.id)
    serializer_class = serializer.DecMethodSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['name']


class WorkRouteViewSet(FalseDeleteModelViewSet):
    """
    作业路线
    """
    def get_queryset(self):
        return models.WorkRoute.objects.all().filter(if_deleted=False, service_provider=self.request.user.company.id)
    serializer_class = serializer.WorkRouteSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ["name"]
    ordering_fields = ["name"]


class CtnSizeViewSet(FalseDeleteModelViewSet):
    """
    箱尺寸
    """
    def get_queryset(self):
        return models.CtnSize.objects.all().filter(if_deleted=False, service_provider=self.request.user.company.id)
    serializer_class = serializer.CtnSizeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ["name"]
    ordering_fields = ["name"]


class CtnTypeViewSet(FalseDeleteModelViewSet):
    """
    箱类型
    """
    def get_queryset(self):
        return models.CtnType.objects.all().filter(if_deleted=False, service_provider=self.request.user.company.id)
    serializer_class = serializer.CtnTypeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ["code", "name"]
    ordering_fields = ["name"]


class UnPackTypeListViewSet(FalseDeleteModelViewSet):
    """
    拆箱方式
    """
    def get_queryset(self):
        return models.UnPackType.objects.all().filter(if_deleted=False, service_provider=self.request.user.company.id)
    serializer_class = serializer.UnPackTypeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['name']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用
    ordering_fields = ['name']


class ForkliftViewSet(FalseDeleteModelViewSet):
    """
    叉车车辆
    """
    def get_queryset(self):
        return models.Forklift.objects.all().filter(if_deleted=False, service_provider=self.request.user.company.id)
    serializer_class = serializer.ForkliftSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['no']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用
    ordering_fields = ['no']


class TransModeViewSet(IntegratedPlatformFalseDeleteModelViewSet):
    """
    成交方式
    """
    queryset = models.TransMode.objects.all().filter(if_deleted=False)
    serializer_class = serializer.TransModeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['code', 'name']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用
    ordering_fields = ['id']


class CurrencyViewSet(IntegratedPlatformFalseDeleteModelViewSet):
    """
    币制表
    """
    queryset = models.Currency.objects.all().filter(if_deleted=False)
    serializer_class = serializer.CurrencySerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['code', 'name', 'name_en']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用
    ordering_fields = ['id']


class TransportModeViewSet(IntegratedPlatformFalseDeleteModelViewSet):
    """
    运输方式
    """
    queryset = models.TransportMode.objects.all().filter(if_deleted=False)
    serializer_class = serializer.TransportModeSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['code', 'name']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用
    ordering_fields = ['id']


class CustomsModeViewSet(IntegratedPlatformFalseDeleteModelViewSet):
    """
    关区表
    """
    queryset = models.CustomsMode.objects.all().filter(if_deleted=False)
    serializer_class = serializer.CustomsModeSerializer
    pagination_class = YzPageSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['code', 'name']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用
    ordering_fields = ['id']


class DomesticDestinationViewSet(IntegratedPlatformFalseDeleteModelViewSet):
    """
    境内目的地
    """
    queryset = models.DomesticDestination.objects.all().filter(if_deleted=False)
    serializer_class = serializer.DomesticDestinationSerializer
    pagination_class = YzPageSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['code', 'name']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用


class CountryViewSet(IntegratedPlatformFalseDeleteModelViewSet):
    """
    国家地区代码
    """
    queryset = models.Country.objects.all().filter(if_deleted=False)
    serializer_class = serializer.CountrySerializer
    pagination_class = YzPageSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['code', 'name', 'name_en']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用
    ordering_fields = ['id']


class MeasureViewSet(IntegratedPlatformFalseDeleteModelViewSet):
    """
    计量单位
    """
    queryset = models.Measure.objects.all().filter(if_deleted=False)
    serializer_class = serializer.MeasureSerializer
    pagination_class = YzPageSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['unit', 'unit_name']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用
    ordering_fields = ['id']


class TradeModeViewSet(IntegratedPlatformFalseDeleteModelViewSet):
    """
    贸易方式
    """
    queryset = models.TradeMode.objects.all().filter(if_deleted=False)
    serializer_class = serializer.TradeModeSerializer
    pagination_class = YzPageSetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['code', 'name', 'simple_name']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields配合使用
    ordering_fields = ['id']
