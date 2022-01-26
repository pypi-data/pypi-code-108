from typing import Callable, List, TypeVar, Generic, Tuple

T = TypeVar("T")
NextPageFunction = Callable[[str], Tuple[List[T], str]]


class Pager(Generic[T]):
    """Pager."""

    next_page: NextPageFunction

    def __init__(self, next_page: NextPageFunction):
        self.next_page = next_page

    def __iter__(self):
        return PagerInterator(self)

    def to_list(self) -> List[T]:
        """Convert iterator to list."""
        return list(self)


class PagerInterator(Generic[T]):
    """Creates an iterator form a list operation."""

    def __init__(self, source: Pager[T]):
        self.source = source
        self.next_page_token = ""
        self.current_pointer = 0
        self.current_page = None

    def __next__(self) -> T:

        if self.current_page is None or (
            self.current_pointer == len(self.current_page)
            and self.next_page_token != ""
        ):
            self.current_page, self.next_page_token = self.source.next_page(
                self.next_page_token
            )
            self.current_pointer = 0

        if self.current_pointer < len(self.current_page):
            self.current_pointer += 1
            return self.current_page[self.current_pointer - 1]

        raise StopIteration
