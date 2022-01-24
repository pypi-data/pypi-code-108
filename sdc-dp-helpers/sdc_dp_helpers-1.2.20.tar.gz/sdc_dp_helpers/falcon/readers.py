"""
    CUSTOM FALCON READER CLASSES
"""
import os

import requests

from sdc_dp_helpers.api_utilities.date_managers import date_handler, date_range
from sdc_dp_helpers.api_utilities.file_managers import load_file
from sdc_dp_helpers.api_utilities.retry_managers import request_handler, retry_handler


class CustomFalconReader:
    """
    Custom Falcon Reader
    """
    def __init__(self, creds_file, config_file=None):
        self._creds = load_file(creds_file, "yml")
        self._config = load_file(config_file, "yml")

        self.request_session = requests.Session()

    @retry_handler(exceptions=ConnectionError, total_tries=5)
    def _get_channel_ids(self):
        """
        Gather all available channel ids.
        """
        print("GET: channel ids.")
        url = f"https://api.falcon.io/channels?apikey={self._creds['api_key']}"
        response = self.request_session.get(url=url, params={"limit": "9999"})

        response_data = response.json()
        if response.status_code == 200:
            channel_ids = set()
            for item in response_data.get("items", []):
                channel_ids.add(item["id"])

            return channel_ids

        raise ConnectionError(
            f"Falcon API failed to return channel ids. "
            f"Status code: {response.status_code}, Reason: {response.reason}."
        )

    @request_handler(
        wait=int(os.environ.get("REQUEST_WAIT_TIME", 2)),
        backoff_factor=float(os.environ.get("REQUEST_BACKOFF_FACTOR", 0.01)),
        backoff_method=os.environ.get("REQUEST_BACKOFF_METHOD", 0.01),
    )
    @retry_handler(exceptions=TimeoutError, total_tries=5, initial_wait=900)
    def _get_content_metrics_by_channel_ids(self, channel_id, date):
        """
        Request handler for Falcon metrics by channel.
        """
        print("POST: content metrics.")
        url = f"https://api.falcon.io/measure/api/v1/content/metrics?apikey={self._creds['api_key']}"

        offset = 0
        while True:
            print(f"Channel Id: {channel_id}, Date: {date}, Offset: {offset}.")
            response = self.request_session.get(
                url=url,
                headers={"Content-Type": "application/json"},
                json={
                    "since": date,
                    "until": date,
                    "postsSince": date,
                    "postsUntil": date,
                    "direction": self._config.get("direction", "ASC"),
                    "channels": [channel_id],
                    "metrics": self._config.get("metrics", []),
                    "offset": offset,
                },
            )

            status_code = response.status_code
            reason = response.reason
            if status_code == 200:
                response_data = response.json()
                print(response_data)
                offset += 1
            elif reason == "Not Found" and status_code == 404:
                print(f"No data for channel id: {channel_id}, skipping.\n")
                break
            elif status_code == 429:
                raise TimeoutError("Rolling Window Quota [429] reached.")
            else:
                raise ConnectionError(f"Reason: {reason}, Status: {status_code}.")

    def run_query(self):
        """
        Get metrics by channel Id context returns a request session with the ability
        to page with offsets.
        Content (or Post level) contains all metrics about your specific piece of
        content (posts). Here you will find impressions, reach, likes,
        shares and other metrics that show how well your specific post has performed.
        https://falconio.docs.apiary.io/reference/content-api/get-copied-content.
        """
        channel_ids = self._get_channel_ids()
        print(f"Attempting to gather metrics from {len(channel_ids)} channel ids.")
        for date in date_range(
                start_date=date_handler(self._config.get("since", None), "%Y-%m-%d"),
                end_date=date_handler(self._config.get("until", None), "%Y-%m-%d"),
        ):
            for channel_id in channel_ids:
                self._get_content_metrics_by_channel_ids(channel_id=channel_id, date=date)
