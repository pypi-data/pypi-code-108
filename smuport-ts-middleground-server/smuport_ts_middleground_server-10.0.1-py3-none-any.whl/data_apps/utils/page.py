from rest_framework.pagination import PageNumberPagination

from .mypagination import MyPageNumberPagination


class YzPageSetPagination(PageNumberPagination):
    page_size = 99999
    page_size_query_param = 'pageSize'
    page_query_param = 'pageIndex'
    max_page_size = 99999


class CargoPageSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'pageSize'
    page_query_param = 'pageIndex'
    max_page_size = 24


class InventoryPageSetPagination(MyPageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'
    page_query_param = 'pageIndex'
    max_page_size = 40