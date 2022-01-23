import django_filters
from . import models


class TlmsWmsEntDirectFilter(django_filters.rest_framework.FilterSet):
    """
    入库计划过滤类
    """
    # lookup_expr（可选）为判断条件，field_name（必选）为模型类属性，created_time查询字符串
    # icontains表示模糊查询（包含），并且忽略大小写
    # iexact表示精确匹配, 并且忽略大小写
    # exact表示精确匹配
    id = django_filters.CharFilter(field_name='id', lookup_expr='icontains')
    consignor = django_filters.CharFilter(field_name='consignor')
    start_date = django_filters.DateTimeFilter(field_name='plan_ent_date', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='plan_ent_date', lookup_expr='lte')
    plan_status = django_filters.CharFilter(field_name='plan_status')
    entrust_plan_id = django_filters.CharFilter(field_name='entrust_plan_id')
    ent_plan_id = django_filters.CharFilter(field_name='ent_plan_id')
    stock_type = django_filters.CharFilter(field_name="stock_type")
    stock_bill_type = django_filters.CharFilter(field_name="stock_bill_type")
    bill_type = django_filters.CharFilter(field_name="bill_type")
    business_type = django_filters.CharFilter(field_name="business_type")
    tlms_plan = django_filters.CharFilter(field_name='tlms_plan')
    wms_ent_plan = django_filters.CharFilter(field_name='wms_ent_plan')
    wms_out_plan = django_filters.CharFilter(field_name='wms_out_plan')

    class Meta:
        model = models.TlmsWmsEntDirect
        fields = ['id', 'entrust_plan_id', 'ent_plan_id', 'consignor', 'start_date', 'plan_status', 'end_date',
                  'stock_type', 'stock_bill_type', 'bill_type', 'business_type', 'tlms_plan', 'wms_ent_plan',
                  'wms_out_plan']
