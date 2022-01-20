class QueryModel(object):
    def __init__(self, query=None, sort: dict = None, offset=100, page=0, text=None):
        self.query = query
        self.sort = sort
        self.offset = offset
        self.page = page
        self.text = text


class FullTextModel(object):
    def __init__(self, text=None, sort: dict = None, offset=100, page=0):
        self.text = text
        self.sort = sort
        self.offset = offset
        self.page = page
