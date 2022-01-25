import abc
import functools
import inspect
import sys
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Type,
    TypeVar,
    cast,
)

from globus_sdk.response import GlobusHTTPResponse

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

PageT = TypeVar("PageT", bound=GlobusHTTPResponse)
P = ParamSpec("P")
R = TypeVar("R", bound=GlobusHTTPResponse)
C = TypeVar("C", bound=Callable[..., GlobusHTTPResponse])


# stub for mypy
class _PaginatedFunc(Generic[PageT]):
    _has_paginator: bool
    _paginator_class: Type["Paginator[PageT]"]
    _paginator_items_key: Optional[str]
    _paginator_params: Dict[str, Any]


class Paginator(Iterable[PageT], metaclass=abc.ABCMeta):
    """
    Base class for all paginators.
    This guarantees is that they have generator methods named ``pages`` and ``items``.

    Iterating on a Paginator is equivalent to iterating on its ``pages``.

    :param method: A bound method of an SDK client, used to generate a paginated variant
    :type method: callable
    :param items_key: The key to use within pages of results to get an array of items
    :type items_key: str
    :param client_args: Arguments to the underlying method which are passed when the
        paginator is instantiated. i.e. given ``client.paginated.foo(a, b, c=1)``, this
        will be ``(a, b)``. The paginator will pass these arguments to each call of the
        bound method as it pages.
    :type client_args: tuple
    :param client_kwargs: Keyword arguments to the underlying method, like
        ``client_args`` above. ``client.paginated.foo(a, b, c=1)`` will pass this as
        ``{"c": 1}``. As with ``client_args``, it's passed to each paginated call.
    :type client_kwargs: dict
    """

    def __init__(
        self,
        method: Callable[..., Any],
        *,
        items_key: Optional[str] = None,
        client_args: List[Any],
        client_kwargs: Dict[str, Any],
        # the Base paginator must accept arbitrary additional kwargs to indicate that
        # its child classes could define and use additional kwargs
        **kwargs: Any,
    ):
        self.method = method
        self.items_key = items_key
        self.client_args = client_args
        self.client_kwargs = client_kwargs

    def __iter__(self) -> Iterator[PageT]:
        yield from self.pages()

    @abc.abstractmethod
    def pages(self) -> Iterator[PageT]:
        """``pages()`` yields GlobusHTTPResponse objects, each one representing a page
        of results."""

    def items(self) -> Iterator[Any]:
        """
        ``items()`` of a paginator is a generator which yields each item in each page of
        results.

        ``items()`` may raise a ``ValueError`` if the paginator was constructed without
        identifying a key for use within each page of results. This may be the case for
        paginators whose pages are not primarily an array of data.
        """
        if self.items_key is None:
            raise ValueError(
                "Cannot provide items() iteration on a paginator where 'items_key' "
                "is not set."
            )
        for page in self.pages():
            yield from page[self.items_key]

    @classmethod
    def wrap(cls, method: Callable[P, R]) -> Callable[P, "Paginator[R]"]:
        """
        This is an alternate method for getting a paginator for a paginated method which
        correctly preserves the type signature of the paginated method.

        It should be used on instances of clients and only passed bound methods of those
        clients. For example, given usage

            >>> tc = TransferClient()
            >>> paginator = tc.paginated.endpoint_search(...)

        a well-typed paginator can be acquired with

            >>> tc = TransferClient()
            >>> paginated_call = Paginator.wrap(tc.endpoint_search)
            >>> paginator = paginated_call(...)

        Although the syntax is slightly more verbose, this allows `mypy` and other type
        checkers to more accurately infer the type of the paginator.
        """
        if not inspect.ismethod(method):
            raise TypeError(f"Paginator.wrap can only be used on methods, not {method}")
        if not getattr(method, "_has_paginator", False):
            raise ValueError(f"'{method}' is not a paginated method")

        as_paginated = cast(_PaginatedFunc[PageT], method)
        paginator_class = as_paginated._paginator_class
        paginator_params = as_paginated._paginator_params
        paginator_items_key = as_paginated._paginator_items_key

        @functools.wraps(method)
        def paginated_method(*args: Any, **kwargs: Any) -> Paginator[PageT]:
            return paginator_class(
                method,
                client_args=list(args),
                client_kwargs=kwargs,
                items_key=paginator_items_key,
                **paginator_params,
            )

        return cast(Callable[P, Paginator[R]], paginated_method)


def has_paginator(
    paginator_class: Type[Paginator[PageT]],
    items_key: Optional[str] = None,
    **paginator_params: Any,
) -> Callable[[C], C]:
    """
    Mark a callable -- typically a client method -- as having pagination parameters.
    Usage:

    >>> class MyClient(BaseClient):
    >>>     @has_paginator(MarkerPaginator)
    >>>     def foo(...): ...

    This will mark ``MyClient.foo`` as paginated with marker style pagination.
    It will then be possible to get a paginator for ``MyClient.foo`` via

    >>> c = MyClient(...)
    >>> paginator = c.paginated.foo()
    """

    def decorate(func: C) -> C:
        as_paginated = cast(_PaginatedFunc[PageT], func)
        as_paginated._has_paginator = True
        as_paginated._paginator_class = paginator_class
        as_paginated._paginator_items_key = items_key
        as_paginated._paginator_params = paginator_params

        func.__doc__ = f"""{func.__doc__}

        **Paginated Usage**

        This method supports paginated access. To use the paginated variant, give the
        same arguments as normal, but prefix the method name with ``paginated``, as in

        >>> client.paginated.{func.__name__}(...)

        For more information, see
        :ref:`how to make paginated calls <making_paginated_calls>`.
        """
        return func

    return decorate
