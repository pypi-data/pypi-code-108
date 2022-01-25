class DataFilter:
    page_no: int
    page_size: int
    fields: dict
    order_by: str
    order_direction: str

    def __init__(self, page_no = 0, page_size = 25, fields = {}, order_by = 'created_at', order_direction = 'asc'):
        self.page_no = page_no
        self.page_size = page_size
        self.fields = fields
        self.order_by = order_by
        self.order_direction = order_direction

    @classmethod
    def from_dict(cls, filter: dict):
        filter.setdefault('page_no', 0)
        filter.setdefault('page_size', 25)
        filter.setdefault('order_by', 'created_at')
        filter.setdefault('order_direction', 'asc')
        filter.setdefault('fields', {})

        return cls(**filter)
