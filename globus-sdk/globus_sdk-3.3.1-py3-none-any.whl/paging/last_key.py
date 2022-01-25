from typing import Any, Callable, Dict, Iterator, List, Optional

from .base import PageT, Paginator


class LastKeyPaginator(Paginator[PageT]):
    def __init__(
        self,
        method: Callable[..., Any],
        *,
        items_key: Optional[str] = None,
        client_args: List[Any],
        client_kwargs: Dict[str, Any]
    ):
        super().__init__(
            method,
            items_key=items_key,
            client_args=client_args,
            client_kwargs=client_kwargs,
        )
        self.last_key: Optional[str] = None

    def pages(self) -> Iterator[PageT]:
        has_next_page = True
        while has_next_page:
            if self.last_key:
                self.client_kwargs["last_key"] = self.last_key
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            self.last_key = current_page.get("last_key")
            has_next_page = current_page["has_next_page"]
