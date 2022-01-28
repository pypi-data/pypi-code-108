import threading
from typing import Any, Iterable, Iterator, List, Optional, TypeVar

from typing_extensions import Protocol

from benchling_api_client.types import Response
from benchling_sdk.helpers.logging_helpers import sdk_logger
from benchling_sdk.helpers.response_helpers import model_from_detailed

# TODO BNCH-15439 Make bounded if we can inherit from a common model
ResultsBody = TypeVar("ResultsBody")
Model = TypeVar("Model")
NextToken = str

RESULTS_COUNT_HEADER = "Result-Count"


class PagedApiCall(Protocol):
    """Make an HTTP call which implemented pagination."""

    def __call__(self, next_token: NextToken) -> Response[Any]:
        """Perform an HTTP call, passing the next token from the API."""
        ...


class ResultsExtractor(Protocol):
    """Extract results from a paginated response."""

    def __call__(self, body: Any) -> Optional[List[Any]]:
        """
        Extract a list of modeled results from an HTTP response.

        Typically this entails knowing the attribute in the response which contains the list.
        """
        ...


class TokenExtractor(Protocol):
    """Get the next token."""

    def __call__(self, body: Any) -> NextToken:
        """Extract an API pagination token from an HTTP response."""
        ...


class LengthExtractor(Protocol):
    """Extract estimated size information if available."""

    def __call__(self, response: Response[Model]) -> Optional[int]:
        """Calculate the estimated total size of paginated records."""
        ...


def _default_token_extractor(body: ResultsBody) -> NextToken:
    """
    Extract the `next_token` from a result.

    A default method that returns the `next_token` from a model returned by
    the API. Since the generated API models do not inherit from a common base class,
    the `ResultsBody` type is unbounded.

    :param body: A model returned from the API which should have a `next_token` attribute
    :return: A str of the `next_token` from the results body
    """
    return body.next_token  # type: ignore


def _default_length_extractor(response: Response[Model]) -> Optional[int]:
    """
    Extract the estimated size (length) of total results from a response.

    A default method that returns the estimated length of total available results from the API.
    It will return None if the API did not indicate how many results were available.

    :param response: A response returned from the API
    :return: An optional int containing the estimated length of the results
    """
    if (
        response.headers
        and RESULTS_COUNT_HEADER in response.headers
        and response.headers[RESULTS_COUNT_HEADER].isdigit()
    ):
        return int(response.headers[RESULTS_COUNT_HEADER])
    return None


class PageIterator(Iterable[List[Model]]):
    """
    Paginate arbitrary Benchling API endpoints which support the concept of a `next_token`.

    `next_token` points to subsequent pages of results. Supporting API
    endpoints typically return a "results body" object which contains a key for `next_token`,
    as well as a key for a collection of results representing the current page.

    Any API errors encountered during retrieval of a page will be marshaled to
    :class:`benchling_sdk.errors.BenchlingError`.
    """

    _api_call: PagedApiCall
    _results_extractor: ResultsExtractor
    _token_extractor: TokenExtractor
    _length_extractor: LengthExtractor
    _next_token: Optional[NextToken]
    _approximate_length: Optional[int]
    _first_page: Optional[List[Model]]
    _iterations_count: int
    _forced_iteration: bool
    # Hold a lock since we are relying on internal state that circumvents standard next() behavior
    _lock: threading.Lock

    def __init__(
        self,
        api_call: PagedApiCall,
        results_extractor: ResultsExtractor,
        token_extractor: TokenExtractor = _default_token_extractor,
        length_extractor: LengthExtractor = _default_length_extractor,
    ) -> None:
        """
        Initialize a PageIterator.

        :param api_call: A Callable that accepts a str for the next_token
        :param results_extractor: A Callable that can extract a list of models from a results body
        :param token_extractor: A Callable that can extract the next_token str value from a results body
        :param length_extractor: A Callable that can extract the approximated available results
            count from a response
        """
        self._api_call = api_call
        self._results_extractor = results_extractor
        self._token_extractor = token_extractor
        self._length_extractor = length_extractor
        self._next_token = None
        self._approximate_length = None
        self._first_page = None
        self._iterations_count = 0
        self._forced_iteration = False
        self._lock = threading.Lock()

    def _fetch_data(self) -> List[Model]:
        with self._lock:
            # If we previously fetched the first page without the iterator being advanced, just return the
            # first page
            if self._forced_iteration and self._iterations_count > 0:
                self._forced_iteration = False
                # Appease MyPy with explicit [] return
                return self._first_page if self._first_page else []
            next_token = self._next_token if self._next_token else ""
            response: Response[Model] = self._api_call(next_token)
            result_body: Model = model_from_detailed(response)
            self._approximate_length = self._length_extractor(response)
            self._next_token = self._token_extractor(result_body)
            sdk_logger.debug(
                "Next token: %s Approximate Result Count: %s", self._next_token, self._approximate_length
            )
            data = self._results_extractor(result_body)
            results = [] if data is None else data
            if self._iterations_count == 0:
                self._first_page = results
            self._iterations_count += 1
            return results

    @property
    def next_token(self) -> Optional[NextToken]:
        """Return the last nextToken provided by the API, if applicable."""
        return self._next_token

    @property
    def estimated_count(self) -> int:
        """
        Return the value of the Result-Count header provided by the API, if applicable.

        Some endpoints may not implement this header. In that case, NotImplementedError is raised.
        """
        if self._first_page is None:
            self._forced_iteration = True
            self._first_page = self._fetch_data()
        if self._approximate_length is None:
            raise NotImplementedError("The API does not support Estimated Count for this operation")
        return self._approximate_length

    def first(self) -> Optional[Model]:
        """
        Return the first item from the first page.

        Will return None if the page had zero results.
        Operates independent of iteration - calls to `first` after starting iteration will still
        return the first item from the first page and not the current page.
        """
        if self._first_page is None:
            self._forced_iteration = True
            self._first_page = self._fetch_data()
        if self._first_page and len(self._first_page) > 0:
            return self._first_page[0]
        return None

    def __iter__(self) -> Iterator[List[Model]]:
        return self

    def __next__(self) -> List[Model]:
        if (
            self._next_token is None
            or len(self._next_token) > 0
            or (self._first_page is not None and self._iterations_count == 1 and self._forced_iteration)
        ):
            return self._fetch_data()
        raise StopIteration
