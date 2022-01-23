from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from ..utils.page import YzPageSetPagination
from ..utils.yzModelViewSet import YzModelViewSet
from . import serializer
from . import models
from . import filter
# Create your views here.


class TlmsWmsEntDirectListViewSet(YzModelViewSet):
    """
    入库委托指令
    """
    def get_queryset(self):
        return models.TlmsWmsEntDirect.objects.all().filter(service_provider=self.request.user.company.id)
    serializer_class = serializer.TlmsWmsEntDirectSerializer
    pagination_class = YzPageSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = filter.TlmsWmsEntDirectFilter
    search_fields = ['contract_no', 'b_l_no']  # SearchFilter: like模糊搜索, query params为"search"，与search_fields来配合使用
    ordering_fields = ['lastupdatedt']
    ordering = ['-lastupdatedt']
