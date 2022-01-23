from sqlalchemy import and_, or_
from sqlalchemy.orm.query import Query
from typing import List


class SQLSearch:
    """
    Helper class provides a quick and ez search utility to endpoints
    """
    def __init__(self, search_text: str, column: str = None):
        self.search_text = search_text
        self.column: str = column

    def search(self, model, query: Query, columns: List[str], use_or=True, case_sensitive=False) -> Query:
        if not self.search_text:
            return query

        if len(self.search_text) < 3:
            raise Exception("Search criteria cannot be shorter than 3 characters")

        if self.column:
            if self.column in columns:
                columns = [self.column]
            else:
                raise Exception("Invalid column to filter by")

        filters: list = []

        for column in columns:
            column = getattr(model, column, None)
            if case_sensitive:
                filters.append(
                    column.like('%' + self.search_text + '%')
                )
            else:
                filters.append(
                    column.ilike('%' + self.search_text + '%')
                )

        if use_or:
            return query.filter(or_(*filters))
        else:
            return query.filter(and_(*filters))


class SQLSort:
    """
    Helper class provides a quick and ez sort utility to endpoints
    """
    def __init__(self, column: str, desc: bool=False):
        self.desc: bool = desc
        self.column: str = column

    def sort(self, model, query: Query):
        if not self.column:
            return query

        column = getattr(model, self.column, None)
        if self.desc:
            return query.order_by(column.desc())
        else:
            return query.order_by(column)
