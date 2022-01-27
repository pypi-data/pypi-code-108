# -*- coding: utf-8 -*-
import logging
import math
import random
import time
from collections.abc import Iterator, Sized
from enum import Enum
from urllib.parse import parse_qs, urlsplit

import apistar
import requests

logger = logging.getLogger(__name__)


class PaginationMode(Enum):
    """Pagination modes with their different indexes"""

    PageNumber = "page"
    Cursor = "cursor"


class ResponsePaginator(Sized, Iterator):
    """
    A lazy generator to handle paginated Arkindex API endpoints.
    Does not perform any requests to the API until it is required.
    """

    def __init__(self, client, operation_id, *request_args, **request_kwargs):
        r"""
        :param client apistar.Client: An API client to use to perform requests for each page.
        :param \*request_args: Arguments to send to :meth:`apistar.Client.request`.
        :param \**request_kwargs: Keyword arguments to send to :meth:`apistar.Client.request`.
        """
        self.client = client
        """The APIStar client used to perform requests on each page."""

        self.data = {}
        """Stored data from the last performed request."""

        self.results = []
        """Stored results from the last performed request."""

        self.operation_id = operation_id
        """Client operation"""

        self.request_args = request_args
        """Arguments to send to :meth:`apistar.Client.request` with each request."""

        self.request_kwargs = request_kwargs
        """Keyword arguments to send to :meth:`apistar.Client.request` with each request."""

        self.mode = None
        """`page` for PageNumberPagination endpoints or `cursor` for CursorPagination endpoints."""

        self.count = None
        """Total results count."""

        self.pages_count = None
        """Total pages count."""

        self.pages_loaded = 0
        """Number of pages already loaded."""

        self.retries = request_kwargs.pop("retries", 5)
        assert (
            isinstance(self.retries, int) and self.retries > 0
        ), "retries must be a positive integer"
        """Max number of retries per API request"""

        # First page key is an empty string as we do not know yet the pagination type (e.g. page, cursor)
        self.initial_page = ""
        # Store retrieved pages remaining retries
        self.pages = {self.initial_page: self.retries}

        # Store missing page indexes
        self.missing = set()
        self.allow_missing_data = request_kwargs.pop("allow_missing_data", False)
        assert isinstance(
            self.allow_missing_data, bool
        ), "allow_missing_data must be a boolean"

    def _fetch_page(self):
        # Filter out pages with no retries
        # Transform as a list of tuples for simpler output
        remaining = sorted([(m, v) for m, v in self.pages.items() if v > 0])

        # No remaining pages, end of iteration
        if not remaining:
            raise StopIteration

        # Get next page to load
        index, retry = remaining[0]

        if self.mode:
            self.request_kwargs[self.mode.value] = index

        try:
            extra_kwargs = {}
            if not self.pages_loaded:
                logger.info(
                    f"Loading first page on try {self.retries - retry + 1}/{self.retries}"
                )
                operation_fields = [
                    f.name
                    for f in self.client.lookup_operation(self.operation_id).fields
                ]
                # Ask to count results if the operation handle it as we do not know the pagination mode yet
                if "with_count" in operation_fields:
                    extra_kwargs["with_count"] = "true"
            else:
                logger.info(
                    f"Loading {self.mode.value} {index} on try {self.retries - retry + 1}/{self.retries}"
                    f" - remains {self.pages_count - self.pages_loaded} pages to load."
                )

            # Fetch the next page
            self.data = self.client.request(
                self.operation_id,
                *self.request_args,
                **self.request_kwargs,
                **extra_kwargs,
            )
            self.results = self.data.get("results", [])

            if not self.mode and self.data:
                # Autodetect if this endpoint uses page or cursor pagination
                if self.data.get("number"):
                    self.mode = PaginationMode.PageNumber
                else:
                    self.mode = PaginationMode.Cursor

            if self.count is None and "count" in self.data:
                # Retrieve information on first page with results count
                self.count = self.data["count"]
                if self.count == 0:
                    # Pagination has retrieved 0 results
                    self.pages = {}
                    return
                self.pages_count = math.ceil(self.count / len(self.results))
                logger.info(
                    f"Pagination will load a total of {self.pages_count} pages."
                )
                if self.mode == PaginationMode.PageNumber:
                    # Initialize all pages once
                    self.pages = {
                        i: self.retries for i in range(2, self.pages_count + 1)
                    }
            elif self.mode == PaginationMode.PageNumber:
                # Mark page as loaded on other pages
                del self.pages[index]

            if self.mode == PaginationMode.Cursor:
                # Parse next URL to retrieve the cursor of the next page
                query = urlsplit(self.data["next"]).query
                cursor_query = parse_qs(query).get("cursor")
                if not cursor_query:
                    self.pages = {}
                else:
                    self.pages = {cursor_query[0]: self.retries}

            # Stop happy path here, we don't need to process errors
            self.pages_loaded += 1
            return self.data

        except apistar.exceptions.ErrorResponse as e:
            logger.warning(f"API Error {e.status_code} on pagination: {e.content}")

            # Decrement pages counter
            self.pages[index] -= 1

            # Sleep a bit (less than a second)
            time.sleep(random.random())

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Server connection error, will retry in a few seconds: {e}")

            # Decrement pages counter
            self.pages[index] -= 1

            # Sleep a few seconds
            time.sleep(random.randint(1, 10))

        # Detect and store references to missing pages
        # when a page has no retries left
        if self.pages[index] <= 0:
            error_text = "No more retries left"
            if self.mode:
                error_text += f" for {self.mode.value} {index}"

            logger.warning(error_text)
            if self.allow_missing_data:
                self.missing.add(index)
            else:
                raise Exception("Stopping pagination as data will be incomplete")

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.results) < 1:
            if self.data and self.data.get("next") is None:
                raise StopIteration

            # Continuously try to fetch a page until there are some retries left
            # This will still yield as soon as some data is fetched
            while self._fetch_page() is None:
                pass

        # Even after fetching a new page, if the new page is empty, just fail
        if len(self.results) < 1:
            raise StopIteration

        return self.results.pop(0)

    def __len__(self):
        # Handle calls to len when no requests have been made yet
        if not self.pages_loaded and self.count is None:
            self._fetch_page()
        return self.count

    def __repr__(self):
        return "<{} via {!r}: {!r} {!r}>".format(
            self.__class__.__name__,
            self.client,
            (self.operation_id, self.request_args),
            self.request_kwargs,
        )
