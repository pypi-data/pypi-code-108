from django.db.models import QuerySet


class PaginatorMeta(type):
    def __new__(mcs, name, bases, act):
        mcs.const(name, act)
        return super().__new__(mcs, name, bases, act)

    @staticmethod
    def const(name, act):
        if 'page_param' in act and not isinstance(act['page_param'], str):
            raise TypeError("{}的page_param必须是str类型！".format(name))

        if 'page_size_param' in act and not isinstance(act['page_size_param'], str):
            raise TypeError("{}的page_size_param必须是str类型！".format(name))

        if 'max_page_size' in act and not isinstance(act['max_page_size'], int):
            raise TypeError("{}的max_page_size必须是int类型！".format(name))


class PaginatorBase(metaclass=PaginatorMeta):
    max_page_size = 100
    """适用Django翻页功能"""

    def __init__(self, queryset, page, page_size=None):
        """
        :param queryset:QuerySet
        :param page: 以为整型，也可以是被转为整型的字符串，为None则默认1
        :param page_size: 以为整型，也可以是被转为整型的字符串，为None则默认30
        """
        if not isinstance(queryset, QuerySet):
            raise TypeError("queryset必须是QuerySet对象")
        self._queryset = queryset
        self._total = queryset.count()  # 数据总条数
        # 每页获取条数
        self._page_size = self._process_page_size(page_size)
        # 取整数页，先忽略可能的余数
        page_count = self._total // self._page_size
        # 如果总数能被page_size整数意味着没有余数，否则总页数+1
        self._page_count = page_count if self._total % self._page_size == 0 else page_count + 1  # 总页数
        # _page_count计算完成才能计算page page不能大于_page_count，也不能小于1
        self._page = self._process_page(page)

    def _process_page(self, page):
        """将传进来的page处理成合法值"""
        page = page if page else 1  # 如果传进来None值
        page = self._to_int(page)
        page = min(self._page_count, page)  # 页码不能大于总页数
        page = max(1, page)  # 防止page_count（空数据）为0时，page也为0
        return page

    def _process_page_size(self, page_size):
        page_size = self._to_int(page_size) if page_size else 30
        if self.max_page_size:  # 如果设置了max_size,则不能大于max_size
            page_size = min(page_size, self.max_page_size)
        page_size = min(page_size, self._total)  # page_size不能大于总条数
        # 字符串'0'会引发除0错误
        page_size = max(1, page_size)  # page_size不能小于1
        return page_size

    def sub_set(self):
        page = self._page
        start_index, end_index = (page - 1) * self._page_size, page * self._page_size
        sub_set = self._queryset[start_index:end_index]
        return sub_set

    def _to_int(self, value):
        try:
            return int(value)  # 如果传进来字符串值
        except Exception as err:
            raise ValueError('将{} 转为整型时失败！'.format(str(value)))

    def page_count(self):
        return {'page': self._page,
                'page_size': self._page_size,
                'page_count': self._page_count,
                'total': self._total,
                'pre': None if self._page == 1 else self._page - 1,
                'next': self._page + 1 if self._page < self._page_count else None
                }
