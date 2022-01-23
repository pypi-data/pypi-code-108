import django_filters
from .models import Cargo
from itertools import chain


class CargoFilter(django_filters.rest_framework.FilterSet):
    """
    商品过滤类
    """
    class Meta:
        model = Cargo
        fields = ['name']