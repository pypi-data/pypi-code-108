from .paginator_base import PaginatorBase


class Paginator(PaginatorBase):
    page_param = 'page'  # 查询参数名
    page_size_param = 'page_size'
    max_page_size = 100

    def __init__(self, queryset, request):
        query = request.POST or request.GET
        page = query.get(self.page_param)
        page_size = query.get(self.page_size_param)
        super().__init__(queryset, page, page_size)
