import math

from sqlalchemy.orm.query import Query
from pydantic import BaseModel
from typing import Callable, Union


class Pagination(BaseModel):
    """
    Pagination state
    """
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous_page: bool
    has_next_page: bool
    previous_page: Union[int, None]
    next_page: Union[int, None]


class Page(BaseModel):
    """
    Page state
    """
    items: list
    pagination: Pagination

    def transform(self, transformer: Callable):
        """
        Transforms results from a DB backbone into a Pydantic (or other) object type

        Args:
            transformer (Callable): A function which takes in an input and returns a transformed output

        Returns:
            None

        """
        items: list = self.items
        self.items = []
        for item in items:
            self.items.append(transformer(item))


class PageMaker:
    """
    Automates the process of creating page state
    """
    def __init__(self, items, page: int, page_size: int, total: int):
        self.items: list = items
        self.total: int = total
        self.previous_page: int = None
        self.next_page: int = None
        self.has_previous: bool = page > 1
        self.current_page: int = page

        self.page_size = page_size
        if self.page_size > 100:
            self.page_size = 100

        if self.has_previous:
            self.previous_page = page - 1

        previous_items: int = (page - 1) * page_size
        self.has_next: bool = previous_items + len(items) < total

        if self.has_next:
            self.next_page = page + 1

        self.pages: int = int(math.ceil(total / float(page_size)))

    def make(self) -> Page:
        """
        Makes a new page

        Returns:
            Page: The current page state

        """
        return Page(
            items=self.items,
            pagination=Pagination(
                current_page=self.current_page,
                page_size=self.page_size,
                total_items=self.total,
                total_pages=self.pages,
                has_previous_page=self.has_previous,
                has_next_page=self.has_next,
                previous_page=self.previous_page,
                next_page=self.next_page
            )
        )


class SQLPaginator:
    """
    Use this class to utilize pagination for SQL DBs
    """
    def __init__(self, page: int, page_size: int):
        """

        Args:
            page (int): The page number to return results for
            page_size (int): The number of results to include in a page
        """
        self.page = page
        self.page_size = page_size
        if self.page_size > 100:
            self.page_size = 100

    def paginate(self, query: Query) -> Page:
        """
        Takes in a SQL Alchemy query and paginates the result.

        Args:
            query (Query): This should be a completed query without a limit or offset applied.

        Returns:
            Page: The page state

        """
        if self.page <= 0:
            raise AttributeError('page needs to be >= 1')

        if self.page_size <= 0:
            raise AttributeError('page_size needs to be >= 1')

        items: list = query.limit(self.page_size).offset((self.page - 1) * self.page_size).all()

        # We remove the ordering of the query since it doesn't matter for getting a count and
        # might have performance implications as discussed on this Flask-SqlAlchemy issue
        # https://github.com/mitsuhiko/flask-sqlalchemy/issues/100
        total: int = query.order_by(None).count()

        return PageMaker(items, self.page, self.page_size, total).make()
