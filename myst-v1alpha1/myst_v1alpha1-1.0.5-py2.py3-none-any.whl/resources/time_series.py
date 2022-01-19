"""This module contains the `TimeSeries` resource."""
from collections import OrderedDict

from myst_v1alpha1 import get_client
from myst_v1alpha1.resource import Resource
from myst_v1alpha1.utils.requests_utils import encode_url
from myst_v1alpha1.utils.validation_utils import validate_mutually_exclusive_arguments


class TimeSeries(Resource):
    """The core time series class used for interacting with time series locally and on the Myst Platform."""

    RESOURCE_NAME = "time_series"

    def fetch(
        self, start_time=None, end_time=None, start_offset=None, end_offset=None, as_of_time=None, time_zone=None
    ):
        """Fetches a `TimeSeriesFetchResult` with the given time range parameters.

        Args:
            start_time (datetime.datetime): start time of interval to fetch data for; either `start_time` or
                `start_offset` must be specified
            end_time (datetime.datetime): end time of interval to fetch data for; either `end_time` or
                `end_offset` must be specified
            start_offset (datetime.timedelta): start offset relative to `as_of_time` marking the start of the time
                period to fetch data; either `start_time` or `start_offset` must be specified
            end_offset (datetime.timedelta): end offset relative to `as_of_time` marking the end of the time
                period to fetch data; either `end_time` or `end_offset` must be specified
            as_of_time (datetime.datetime, optional): as of time for which to fetch data for
            time_zone (str or datetime.tzinfo, optional): time zone used to format returned data series timestamps; if
                not specified, defaults to UTC

        Returns:
            data (dict): time series data

        Raises:
            ValueError: Either `start_time` or `start_offset` must be specified.
            ValueError: Either `end_time` or `end_offset` must be specified.
            ValueError: Only one of `start_time` and `start_offset` cannot be specified.
        """
        # Validate arguments.
        start_param = validate_mutually_exclusive_arguments(
            OrderedDict(start_time=start_time, start_offset=start_offset), require_one=True
        )
        end_param = validate_mutually_exclusive_arguments(
            OrderedDict(end_time=end_time, end_offset=end_offset), require_one=True
        )

        # Get global default client to make request with.
        client = get_client()

        # Add non `None` parameters to request param list.
        params = [start_param, end_param]
        if as_of_time is not None:
            params.append(("as_of_time", as_of_time))

        if time_zone is not None:
            params.append(("time_zone", time_zone))

        # Make request and parse the response.
        endpoint = encode_url(base_url="{instance_url}:fetch".format(instance_url=self.instance_url()), params=params)
        time_series_fetch_result = client.get(endpoint)

        return time_series_fetch_result

    def fetch_data_series(
        self, start_time=None, end_time=None, start_offset=None, end_offset=None, as_of_time=None, time_zone=None
    ):
        """Fetches raw time series data with the given time range parameters.

        Note that is just a convenience wrapper for `TimeSeries.fetch` that returns the data series from the returned
        `TimeSeriesFetchResult.`

        Args:
            start_time (datetime.datetime): start time of interval to fetch data for; either `start_time` or
                `start_offset` must be specified
            end_time (datetime.datetime): end time of interval to fetch data for; either `end_time` or
                `end_offset` must be specified
            start_offset (datetime.timedelta): start offset relative to `as_of_time` marking the start of the time
                period to fetch data; either `start_time` or `start_offset` must be specified
            end_offset (datetime.timedelta): end offset relative to `as_of_time` marking the end of the time
                period to fetch data; either `end_time` or `end_offset` must be specified
            as_of_time (datetime.datetime, optional): as of time for which to fetch data for
            time_zone (str or datetime.tzinfo, optional): time zone used to format returned data series timestamps; if
                not specified, defaults to UTC

        Returns:
            data_series (dict): data series
        """
        time_series_fetch_result = self.fetch(
            start_time=start_time,
            end_time=end_time,
            start_offset=start_offset,
            end_offset=end_offset,
            as_of_time=as_of_time,
            time_zone=time_zone,
        )
        data_series = time_series_fetch_result["data_series"]
        return data_series
