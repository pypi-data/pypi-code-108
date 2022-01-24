# pylint: disable=no-self-use
import json
import time
import warnings
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from urllib.error import URLError

import pandas as pd
import requests

from sdc_dp_helpers.api_utilities.date_managers import date_handler
from sdc_dp_helpers.api_utilities.file_managers import load_file
from sdc_dp_helpers.api_utilities.retry_managers import retry_handler, request_handler


class CustomOneSignalReader:
    def __init__(self, creds_file, config_file=None):
        self._creds = load_file(creds_file, "yml")
        self._config = load_file(config_file, "yml")

        self._header = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {self._creds.get('api_key')}",
            "User-Agent": "Mozilla/5.0",
        }

        self._request_session = requests.Session()
        self.offset, self.data_set = 0, []

    # ConnectionError should be intentional and are handled with a retry
    # anything else is an unexpected issue that should not be retried but raised
    @retry_handler(exceptions=ConnectionError, total_tries=10, should_raise=True)
    def _csv_export_query(self):
        """
        Query handler for csv_export.
        https://documentation.onesignal.com/reference/csv-export

        Generate a compressed CSV export of all of your current user data.
        This method can be used to generate a compressed CSV export of all
        of your current user data. It is a much faster alternative than
        retrieving this data using the /players API endpoint.
        The file will be compressed using GZip.
        The file may take several minutes to generate depending on the number
        of users in your app.
        The URL generated will be available for 3 days and includes random v4
        uuid as part of the resource name to be unguessable.

        ⚠ Note that adding any date oriented payload drastically affects
        the output data. Even if the payload values are null.
        """
        print("POST: csv_export.")
        # response is not always successful for some reason, so retry handler
        # handles the missing "csv_file_url" key response
        response: dict = self._request_session.post(
            url="https://onesignal.com/api/v1/players/csv_export",
            headers=self._header,
            json={"app_id": self._creds.get("app_id")},
        ).json()

        # status code is not always returned, so handling error strings instead
        errors = response.get("errors", [None])[0]
        if errors:
            # The header is definitely valid, so we must assume the app_id is not
            if (
                    errors
                    == "app_id not found. You may be missing a Content-Type: application/json header."
            ):
                raise ConnectionError(
                    "App Id may not be valid or removed from the account."
                )

            # Seems like we are restricted to making one query at a time for a given user, so wait 5 minutes
            if (
                    errors
                    == "User already running another CSV export. Please wait until your other CSV exporter finishes and try again."
            ):
                time.sleep(300)  # the reader may try again after the 5 minute wait
                raise ConnectionError(errors)

            # Raise all other unknown errors in a standard fashion
            raise ConnectionError(errors)
        else:
            print("No errors raised, fetching url.")

        response = response["csv_file_url"]
        attempts = 0
        while True:
            try:
                # Making use of pandas to stream the
                # compressed csv data directly to a df
                _date_fmt = "%Y-%m-%d"
                data_frame: pd.DataFrame = pd.read_csv(response)

                # added functionality to filter results by created_at
                # note the filter can not exceed the last 30 days
                sd = date_handler(self._config.get("start_date", None), _date_fmt)
                ed = date_handler(self._config.get("end_date", None), _date_fmt)
                if sd is not None and ed is not None:
                    # using a temp date field to select relevant data before dropping
                    data_frame["tmp_date"] = pd.to_datetime(data_frame["created_at"])
                    data_frame["tmp_date"] = data_frame["tmp_date"].dt.strftime(
                        _date_fmt
                    )
                    data_frame = data_frame[
                        (
                                data_frame["tmp_date"]
                                >= datetime.strptime(sd, _date_fmt).strftime(_date_fmt)
                        )
                        & (
                                data_frame["tmp_date"]
                                <= datetime.strptime(ed, _date_fmt).strftime(_date_fmt)
                        )
                        ]
                    data_frame.drop("tmp_date", axis="columns", inplace=True)
                break
            except URLError:
                # max wait time is 15 minutes at 10 attempts before
                # we need to contact Onesignal.
                # these attempts are NOT traditional retry attempts
                # so are not handed by @retry_handler.
                print(f"Waiting for file to generate, attempt {attempts}.")
                time.sleep(90)

            attempts += 1

            if attempts >= 10:
                raise FileExistsError(
                    f"Csv file could not be generated, contact Onesignal support. "
                    f"Response {response}."
                )

        return data_frame.to_json(orient="records")

    def _get_view_notification_payloads(self):
        """
        Generate all payloads for the request methods.
        """
        print("GET: view_notifications.")
        initial_response = self._request_session.get(
            url="https://onesignal.com/api/v1/notifications",
            headers=self._header,
            json={"app_id": self._creds.get("app_id")},
        )

        if initial_response.status_code == 200:
            print(f"Connection made: {initial_response.status_code} and {initial_response.reason}.")
            payloads, offsets = [], initial_response.json().get("total_count")
            print(f"Total offsets: {offsets}.")
            if offsets > 0:
                for offset in range(0, offsets):
                    payloads.append({"app_id": self._creds.get("app_id"), "offset": offset})
                return payloads
            else:
                return None

        if initial_response.status_code >= 500:
            raise ConnectionError(
                f"Connection failed with {initial_response.status_code} and connection closed due to a timeout."
            )

        raise ConnectionError(
            f"Connection failed with {initial_response.status_code} and {initial_response.reason}."
        )

    # Onesignal suggest a 60 second wait for any errors above 500,
    # these are internal timeouts that they are aware of.
    @request_handler()
    @retry_handler(exceptions=ConnectionError, total_tries=10, should_raise=True, initial_wait=60, backoff_factor=1)
    def _view_notifications_get(self, payload):
        """
        Standard view notifications get request handler.
        """
        resp = self._request_session.get(
            url="https://onesignal.com/api/v1/notifications",
            headers=self._header,
            json=payload,
        )
        print(f"Payload: {payload}. Status: {resp.status_code} - {resp.reason}.")
        if resp.status_code == 200:
            data_response = resp.json().get("notifications", None)
            if data_response is not None:
                return data_response
            return None
        else:
            raise ConnectionError(f"Connection failed with {resp.status_code} and {resp.reason}.")

    def _view_notifications_query(self):
        """
        Query handler for view_notifications.
        https://documentation.onesignal.com/reference/view-notifications

        View the details of multiple notifications.
        OneSignal periodically deletes records of API notifications
        older than 30 days.
        If you would like to export all notification data to CSV,
        you can do this through the dashboard.

        ⚠ Note that adding any date oriented payload drastically affects
        the output data. Even if the payload values are null.

        With this method comes the option of running a ThreadPoolExecutor
        that will query the payloads in batches of 10. Making the response
        a lot quicker and reducing the change of timeouts and intermittent
        connection issues from the server.
        Python threads are really only useful for concurrent I/O operations.

        WARNING: Setting too many threads will result in a request error
                 of too many connection attempts.
        """
        json_payloads = self._get_view_notification_payloads()
        parallel = self._config.get("parallel", False)
        print(f"Parallel connection: {parallel}.")
        if json_payloads is not None:
            if parallel:
                # Run concurrent connections.
                max_threads = self._config.get("max_threads", 15)
                if max_threads >= 20:
                    warnings.warn(
                        "Too many threads. Onesignal Connection failed with 429 and Too Many Requests could be raised."
                    )
                with ThreadPoolExecutor(max_workers=max_threads) as pool:
                    # append all responses to the dataset
                    data_set = pool.map(self._view_notifications_get, json_payloads)
                    for data in data_set:
                        for row in data:
                            self.data_set.append(row)
            else:
                # Run a stock-standard request process.
                for payload in json_payloads:
                    self.data_set.append(
                        self._view_notifications_get(payload)
                    )

        return json.dumps(self.data_set)

    def run_query(self):
        """
        The Onesignal API provides programmatic methods to
        access data in Onesignal for view_notifications and csv_exports.
        """
        _endpoint = self._config.get("endpoint")
        _parallel = self._config.get("parallel", False)
        if _endpoint == "csv_export":
            return self._csv_export_query()
        elif _endpoint == "view_notifications":
            return self._view_notifications_query()
        else:
            raise EnvironmentError(f"Endpoint {_endpoint} is not supported.")
