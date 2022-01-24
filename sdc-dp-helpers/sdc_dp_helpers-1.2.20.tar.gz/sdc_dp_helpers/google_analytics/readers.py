"""
    CUSTOM READERS CLASSES
        - Class which manages reader tasks like auth, requests, pagination
"""
import datetime
import os
import socket
import sys
from typing import Callable

import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

from sdc_dp_helpers.api_utilities.file_managers import load_file
from sdc_dp_helpers.api_utilities.retry_managers import request_handler, retry_handler
from sdc_dp_helpers.api_utilities.tracking_metadata import tracking_metadata


class GAV3Reader:
    def __init__(
            self, service_account_email, creds_filepath, config_filepath, **kwargs
    ):
        self.service_account_email = service_account_email
        self.creds_filepath = creds_filepath
        self.scopes = kwargs.get(
            "scopes", ["https://www.googleapis.com/auth/analytics.readonly"]
        )

        self.config = load_file(config_filepath, "yaml")
        self.tracking_object = []

    def _get_service(self):
        """
        Get a service that communicates to a Google API.
        """
        credentials = ServiceAccountCredentials.from_p12_keyfile(
            filename=self.creds_filepath,
            scopes=self.scopes,
            service_account_email=self.service_account_email,
        )

        service = build(serviceName="analytics", version="v3", credentials=credentials)

        return service

    @staticmethod
    def _normalize_data(report):
        """
        Flattens the response data to a standard dict.
        """
        headers = [head["name"] for head in report["columnHeaders"]]
        profile = report["profileInfo"]

        data_set = []
        for row in report["rows"]:
            tmp = dict(zip(headers, row))
            tmp.update(profile)
            data_set.append(tmp)

        return data_set

    @request_handler(wait=0.5, backoff_factor=0.1)
    @retry_handler(exceptions=(socket.timeout, HttpError), total_tries=5, initial_wait=60, backoff_factor=2)
    def _query_handler(self, view_id, service, start_index):
        """
        Separated query method to handle retry and delay methods.
        """
        print(f"Querying View ID: {view_id}. At index: {start_index}.")
        response = (
            service.data()
                .ga()
                .get(
                ids=f"ga:{view_id}",
                start_date=self.config.get("start_date"),
                end_date=self.config.get("end_date"),
                # convert mets and dims into comma separated string
                metrics=",".join(self.config.get("metrics", [])),
                dimensions=",".join(self.config.get("dimensions", [])),
                sort=self.config.get("sort", None),
                filters=self.config.get("filters", None),
                max_results=self.config.get("max_results", 5000),
                start_index=start_index,
                samplingLevel="HIGHER_PRECISION",
                include_empty_rows=True,
            )
        )

        # tracking reader progress
        self.tracking_object = tracking_metadata(
            data_object=self.tracking_object,
            service="google_analytics_v3",
            response_datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            index=start_index,
            id_name="view_id",
            id_value=view_id,
            config_datetime=self.config.get("start_date"),
            configuration=self.config,
            byte_size=sys.getsizeof(response),
        )

        return response.execute()

    def run_query(self):
        """
        Core V3 Reporting API.
        The method will try each query 5 times before failing.
        Config File:
            start_date: |
              Start date for fetching Analytics data.
              Requests can specify a start date formatted as YYYY-MM-DD,
              or as a relative date (e.g., today, yesterday, or
              NdaysAgo where N is a positive integer).
            end_date: |
              End date for fetching Analytics data.
              Request can specify an end date formatted as YYYY-MM-DD,
              or as a relative date (e.g., today, yesterday, or
              NdaysAgo where N is a positive integer).
            metrics: A maximum of 10 Metrics in list form.
            dimensions: A maximum of 7 Dimensions in list form.
            sort: |
              A list of comma-separated dimensions and metrics
              indicating the sorting order and sorting direction for the returned data.
            filters: Dimension or metric filters that restrict the data returned for your request.
            view_ids: |
              A list of the unique table ID of the form ga:XXXX, where XXXX is the
              Analytics view (profile) ID for which the query will retrieve the data.
        """
        for view_id in self.config.get("view_ids"):
            data_set = []
            service = self._get_service()  # new service for each view_id
            page_token = 1  # handle paging of response
            while True:
                response = self._query_handler(
                    service=service, view_id=view_id, start_index=page_token
                )
                if len(response.get("rows", [])) < 1:
                    print("No more data in response.")
                    break
                page_token += response.get("itemsPerPage", 0)
                data_set.append(self._normalize_data(response))

            yield data_set


class BaseGAV4Reader:
    """
    Base Google Analytics V4 reader class.

    Used as basis for building custom GA V4 readers, it requires that you
    add your own Authentication through the auth_credentials method.
    The basic workflow is:
    (1) Create credentials
    (2) Build google service object
    (3) Return an iterable of the get_report method
    (4) Iterate until no pagination token is found. A.k.a. pageToken==None
    """

    analytics = None
    max_pages = None

    class ReaderIter:
        """Inner Class - Iterator that yields queries until max pages or pageToken == None."""

        page_counter = 0

        def __init__(
                self, *, query_fn: Callable, query: list, page_token: str = None, **kwargs
        ):
            self.query_fn = query_fn
            self.max_pages = kwargs.get("max_pages", None)
            self.page_token = page_token
            self.query = query

        def __iter__(self):
            """Iterator method for iterator class"""
            return self

        def __next__(self):
            """
            Next method for iterator class which includes
            the StopIteration criteria for iterable
            """
            # check StopIteration criteria
            if self.max_pages is not None:
                if self.page_counter >= self.max_pages:
                    print("stopping iteration on max pages = {}".format(self.max_pages))
                    raise StopIteration

            if self.page_counter > 0 and self.page_token is None:
                print("stopping iteration on pageToken = {}".format(self.page_token))
                raise StopIteration

            # run get_report
            report, self.page_token = self.query_fn(
                queries=self.query, page_token=self.page_token
            )
            print(
                "Finished query function for page {page} of view ID {view_id}".format(
                    page=self.page_counter + 1, view_id=self.query[0].get("viewId")
                )
            )

            # increment pagination counter
            self.page_counter += 1

            return report

    # pylint: disable=no-member
    def build_analytics_service_object(
            self, api_name: str = "analyticsreporting", api_version: str = "v4"
    ):
        """Initializes the analytics reporting service object.
        args:
        client_secrets_path (json) : Google API OAuth2 API credentials
        scopes (list or iterable) : scopes for Google OAuth2 authentication

        Returns:
        analytics an authorized analyticsreporting service object.
        """
        # authorize HTTP object
        http = self.credentials.authorize(http=httplib2.Http())
        # Build the service object.
        return build(api_name, api_version, http=http)

    @request_handler(
        wait=int(os.environ.get("REQUEST_WAIT_TIME", 0)),
        backoff_factor=float(os.environ.get("REQUEST_BACKOFF_FACTOR", 0.01)),
        backoff_method=os.environ.get("REQUEST_BACKOFF_METHOD", 0.01),
    )
    def get_report(self, queries: list, page_token: str = None):
        """
        Use the Analytics Service Object to query the Analytics Reporting API V4.

        args:
        analytics : analytics reporting service object
        query (list): array of queries. [max. 5]
        page_token (str): token sent denoting the last scraped data point
        return:
        analytics report data (json)

        """
        if page_token is not None:
            for query in queries:
                query.update({"page_token": page_token})

        # run batch query
        report = (
            self.analytics.reports()
                .batchGet(body={"reportRequests": queries})
                .execute()
                .get("reports")
        )
        page_token = report[0].get("nextPageToken")

        return report, page_token

    def run_query(self, query: list, page_token: str = None):
        """
        returns a sync iterator
        """
        iter_ = self.ReaderIter(
            query_fn=self.get_report,
            query=query,
            max_pages=self.max_pages,
            page_token=page_token,
        )
        return iter_


class CustomGoogleAnalyticsReaderWithServiceAcc(BaseGAV4Reader):
    """
    Custom Google Analytics Reader which authenticates with Service account
    """

    # pylint: disable=super-init-not-called
    def __init__(
            self,
            service_account_secrets_path: str,
            service_account_email: str,
            scopes: list,
            **kwargs,
    ):
        self.max_pages = kwargs.get("max_pages", None)
        self.credentials = self.auth_credentials(
            service_account_secrets_path, service_account_email, scopes
        )
        # build analytics object
        self.analytics = self.build_analytics_service_object()

    @staticmethod
    def auth_credentials(service_account_secrets_path, service_account_email, scopes):
        """Get a service that communicates to a Google API.
        Args:
            service_account_secrets_path: The filepath to service secrets.
            api_name: The name of the api to connect to.
            api_version: The api version to connect to.
            scope: A list auth scopes to authorize for the application.
            key_file_location: The path to a valid service account p12 key file.
            service_account_email: The service account email address.
            scopes: Allowed scopes for the given credentials
        Returns:
            A service that is connected to the specified API.
        """
        return ServiceAccountCredentials.from_p12_keyfile(
            service_account_email, service_account_secrets_path, scopes=scopes
        )
