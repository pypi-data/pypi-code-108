class SearchFilter(object):

    def __init__(self, field: str, type: str, values: list):
        self.field = field
        self.type = type
        self.values = values


class SearchOrder(object):

    def __init__(self, field: str, type: str):
        self.field = field
        self.type = type


class SearchPagination(object):

    def __init__(self, page: int = 0, size: int = 50):
        self.page = page
        self.size = size


class Search(object):

    def __init__(self):
        self.filter = []
        self.order = []
        self.pagination = SearchPagination()

    def add_filter(self, filter_field: str, filter_type: str, filter_values: list):
        self.filter.append(
            SearchFilter(
                filter_field,
                filter_type,
                filter_values
            )
        )

    def add_multiple_filters(self, filter: SearchFilter):
        for item in filter:
            self.filter.append(
                SearchFilter(
                    item[0],
                    item[1],
                    item[2]
                )
            )

    def add_order(self, order_field: str, order_type: str):
        self.order.append(
            SearchOrder(
                order_field,
                order_type
            )
        )

    def set_pagination(self, page: int = 0, size: int = 50):
        self.pagination = SearchPagination(
            page,
            size
        )
