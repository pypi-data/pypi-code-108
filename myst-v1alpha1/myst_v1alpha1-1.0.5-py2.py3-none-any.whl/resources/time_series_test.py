import datetime

import pytz
import responses

from myst_v1alpha1.resource_test import ResourceTest
from myst_v1alpha1.resources.time_series import TimeSeries


class TimeSeriesTest(ResourceTest):

    _RESOURCE_CLS = TimeSeries
    _RESOURCE_KWARGS = dict(
        object="TimeSeries", title="My Time Series", create_time="2018-01-01T00:00:00Z", update_time=None
    )
    _RESOURCE_GET_JSON = {
        "object": "TimeSeries",
        "uuid": "7e7de7a2-3de3-45e5-bf94-40374a0f8d14",
        "title": "My Time Series",
        "create_time": "2018-01-01T00:00:00Z",
        "update_time": None,
    }
    _RESOURCE_LIST_JSON = {"data": [_RESOURCE_GET_JSON]}
    _EXAMPLE_FETCH_RESULT = {
        "object": "TimeSeriesFetchResult",
        "uuid": "4019e231-4f41-445c-9499-149d59d64dc5",
        "data_series": {
            "2019-01-01T00:00:00Z": -14.3890757468198,
            "2019-01-01T01:00:00Z": -6.57728772551002,
            "2019-01-01T02:00:00Z": 2.77139392215585,
            "2019-01-01T03:00:00Z": 12.4580712230353,
        },
        "create_time": "2019-01-01T00:00:05Z",
        "update_time": None,
    }

    def test_resource(self):
        # Generate a time series to test with.
        time_series = self._generate_resource(uuid="7e7de7a2-3de3-45e5-bf94-40374a0f8d14")

        # Test time series attributes.
        self.assertEqual(time_series.uuid, "7e7de7a2-3de3-45e5-bf94-40374a0f8d14")
        self.assertEqual(time_series.object, "TimeSeries")
        self.assertEqual(time_series.title, "My Time Series")
        self.assertEqual(time_series.create_time, "2018-01-01T00:00:00Z")
        self.assertEqual(time_series.update_time, None)

    def test_class_url(self):
        self.assertEqual(TimeSeries.class_url(), "https://api.myst.ai/v1alpha1/time_series")

    def test_instance_url(self):
        time_series = self._generate_resource(uuid="7e7de7a2-3de3-45e5-bf94-40374a0f8d14")
        self.assertEqual(
            time_series.instance_url(), "https://api.myst.ai/v1alpha1/time_series/7e7de7a2-3de3-45e5-bf94-40374a0f8d14"
        )

    @responses.activate
    def test_resource_get(self):
        # Mock response.
        responses.add(
            responses.GET,
            "https://api.myst.ai/v1alpha1/time_series/7e7de7a2-3de3-45e5-bf94-40374a0f8d14",
            json=self._RESOURCE_GET_JSON,
        )
        time_series = TimeSeries.get(uuid="7e7de7a2-3de3-45e5-bf94-40374a0f8d14")

        # Test that example resource attributes were updated as expected.
        self.assertEqual(time_series.uuid, "7e7de7a2-3de3-45e5-bf94-40374a0f8d14")
        self.assertEqual(time_series.object, "TimeSeries")
        self.assertEqual(time_series.create_time, "2018-01-01T00:00:00Z")
        self.assertEqual(time_series.update_time, None)
        self.assertEqual(time_series.title, "My Time Series")

    @responses.activate
    def test_resource_list(self):
        # Mock example resource response.
        responses.add(
            responses.GET,
            "https://api.myst.ai/v1alpha1/{resource_name}".format(resource_name=self._RESOURCE_CLS.RESOURCE_NAME),
            json=self._RESOURCE_LIST_JSON,
        )

        self.assertEqual(
            TimeSeries.list(),
            [
                TimeSeries(
                    object="TimeSeries",
                    uuid="7e7de7a2-3de3-45e5-bf94-40374a0f8d14",
                    title="My Time Series",
                    create_time="2018-01-01T00:00:00Z",
                    update_time=None,
                )
            ],
        )

    @responses.activate
    def test_resource_refresh(self):
        # Mock response.
        responses.add(
            responses.GET,
            "https://api.myst.ai/v1alpha1/time_series/7e7de7a2-3de3-45e5-bf94-40374a0f8d14",
            json=self._RESOURCE_GET_JSON,
        )

        # Generate an example resource to test with.
        time_series = self._generate_resource(uuid="7e7de7a2-3de3-45e5-bf94-40374a0f8d14")
        time_series.refresh()

        # Test that example resource attributes were updated as expected.
        self.assertEqual(time_series.object, "TimeSeries")
        self.assertEqual(time_series.uuid, "7e7de7a2-3de3-45e5-bf94-40374a0f8d14")
        self.assertEqual(time_series.title, "My Time Series")
        self.assertEqual(time_series.create_time, "2018-01-01T00:00:00Z")
        self.assertEqual(time_series.update_time, None)

    def test_resources_refresh_with(self):
        # Generate an example resource to test with.
        example_resource = self._generate_resource(uuid="c3f3c13b-353b-4df3-b22e-7d3ec2b7a260")

        # Test that example resource attributes were intialized as expected.
        self.assertEqual(example_resource.uuid, "c3f3c13b-353b-4df3-b22e-7d3ec2b7a260")
        self.assertEqual(example_resource.title, "My Time Series")

        example_resource.refresh_with(self._RESOURCE_GET_JSON)

        # Test that example resource attributes were updated as expected.
        self.assertEqual(example_resource.uuid, "7e7de7a2-3de3-45e5-bf94-40374a0f8d14")
        self.assertEqual(example_resource.object, "TimeSeries")
        self.assertEqual(example_resource.create_time, "2018-01-01T00:00:00Z")
        self.assertEqual(example_resource.update_time, None)
        self.assertEqual(example_resource.title, "My Time Series")

    @responses.activate
    def test_time_series_fetch(self):
        # Mock response
        responses.add(
            responses.GET,
            "https://api.myst.ai/v1alpha1/time_series/7e7de7a2-3de3-45e5-bf94-40374a0f8d14:fetch",
            json=self._EXAMPLE_FETCH_RESULT,
        )

        # Generate an example resource to test with.
        time_series = self._generate_resource(uuid="7e7de7a2-3de3-45e5-bf94-40374a0f8d14")

        # Test `TimeSeries.fetch` raises when passed a variety of different invalid argument combinations.
        for start_time, end_time, start_offset, end_offset in [
            (None, None, None, None),
            (datetime.datetime(2019, 1, 1), None, datetime.timedelta(hours=1), None),
            (None, datetime.datetime(2019, 1, 3), None, datetime.timedelta(hours=3)),
            (
                datetime.datetime(2019, 1, 1),
                datetime.datetime(2019, 1, 3),
                datetime.timedelta(hours=1),
                datetime.timedelta(hours=3),
            ),
        ]:

            with self.assertRaises(ValueError):
                time_series.fetch(
                    start_time=start_time, end_time=end_time, start_offset=start_offset, end_offset=end_offset
                )

        # Test `TimeSeries.fetch` just passing in an absolute `start_time` and `end_time`.
        self.assertEqual(
            time_series.fetch(
                # Note that these timestamps don't match response.
                start_time=pytz.utc.localize(datetime.datetime(2019, 1, 1)),
                end_time=pytz.utc.localize(datetime.datetime(2019, 1, 1, 3)),
            ),
            {
                "object": "TimeSeriesFetchResult",
                "uuid": "4019e231-4f41-445c-9499-149d59d64dc5",
                "data_series": {
                    "2019-01-01T00:00:00Z": -14.3890757468198,
                    "2019-01-01T01:00:00Z": -6.57728772551002,
                    "2019-01-01T02:00:00Z": 2.77139392215585,
                    "2019-01-01T03:00:00Z": 12.4580712230353,
                },
                "create_time": "2019-01-01T00:00:05Z",
                "update_time": None,
            },
        )

        self.assertEqual(
            responses.mock.calls[0].request.url,
            (
                "https://api.myst.ai/v1alpha1/time_series/7e7de7a2-3de3-45e5-bf94-40374a0f8d14:fetch?"
                "start_time=2019-01-01T00%3A00%3A00Z&end_time=2019-01-01T03%3A00%3A00Z"
            ),
        )

        # Test `TimeSeries.fetch` passing in an `as_of_time`, too.
        self.assertEqual(
            time_series.fetch(
                # Note that these timestamps don't match response.
                start_time=pytz.utc.localize(datetime.datetime(2019, 1, 1)),
                end_time=pytz.utc.localize(datetime.datetime(2019, 1, 1, 3)),
                as_of_time=pytz.utc.localize(datetime.datetime(2019, 1, 1)),
            ),
            {
                "object": "TimeSeriesFetchResult",
                "uuid": "4019e231-4f41-445c-9499-149d59d64dc5",
                "data_series": {
                    "2019-01-01T00:00:00Z": -14.3890757468198,
                    "2019-01-01T01:00:00Z": -6.57728772551002,
                    "2019-01-01T02:00:00Z": 2.77139392215585,
                    "2019-01-01T03:00:00Z": 12.4580712230353,
                },
                "create_time": "2019-01-01T00:00:05Z",
                "update_time": None,
            },
        )

        self.assertEqual(
            responses.mock.calls[1].request.url,
            (
                "https://api.myst.ai/v1alpha1/time_series/7e7de7a2-3de3-45e5-bf94-40374a0f8d14:fetch?"
                "start_time=2019-01-01T00%3A00%3A00Z&end_time=2019-01-01T03%3A00%3A00Z"
                "&as_of_time=2019-01-01T00%3A00%3A00Z"
            ),
        )

        # Test `TimeSeries.fetch` just passing in an relative `start_offset` and `end_offset`.
        self.assertEqual(
            time_series.fetch(
                # Note that these timestamps don't match response.
                start_offset=datetime.timedelta(hours=1),
                end_offset=datetime.timedelta(hours=3),
            ),
            {
                "object": "TimeSeriesFetchResult",
                "uuid": "4019e231-4f41-445c-9499-149d59d64dc5",
                "data_series": {
                    "2019-01-01T00:00:00Z": -14.3890757468198,
                    "2019-01-01T01:00:00Z": -6.57728772551002,
                    "2019-01-01T02:00:00Z": 2.77139392215585,
                    "2019-01-01T03:00:00Z": 12.4580712230353,
                },
                "create_time": "2019-01-01T00:00:05Z",
                "update_time": None,
            },
        )
        self.assertEqual(
            responses.mock.calls[2].request.url,
            (
                "https://api.myst.ai/v1alpha1/time_series/7e7de7a2-3de3-45e5-bf94-40374a0f8d14:fetch?"
                "start_offset=1%3A00%3A00&end_offset=3%3A00%3A00"
            ),
        )

        # Test `TimeSeries.fetch` just passing in an relative `start_offset` and an absolute `end_time`.
        self.assertEqual(
            time_series.fetch(
                # Note that these timestamps don't match response.
                start_offset=datetime.timedelta(hours=1),
                end_time=pytz.utc.localize(datetime.datetime(2019, 1, 1, 3)),
            ),
            {
                "object": "TimeSeriesFetchResult",
                "uuid": "4019e231-4f41-445c-9499-149d59d64dc5",
                "data_series": {
                    "2019-01-01T00:00:00Z": -14.3890757468198,
                    "2019-01-01T01:00:00Z": -6.57728772551002,
                    "2019-01-01T02:00:00Z": 2.77139392215585,
                    "2019-01-01T03:00:00Z": 12.4580712230353,
                },
                "create_time": "2019-01-01T00:00:05Z",
                "update_time": None,
            },
        )
        self.assertEqual(
            responses.mock.calls[3].request.url,
            (
                "https://api.myst.ai/v1alpha1/time_series/7e7de7a2-3de3-45e5-bf94-40374a0f8d14:fetch?"
                "start_offset=1%3A00%3A00&end_time=2019-01-01T03%3A00%3A00Z"
            ),
        )

        # Test `TimeSeries.fetch` just passing in a `time_zone`.
        self.assertEqual(
            time_series.fetch(
                # Note that these timestamps don't match response.
                start_time=pytz.utc.localize(datetime.datetime(2019, 1, 1)),
                end_time=pytz.utc.localize(datetime.datetime(2019, 1, 1, 3)),
                time_zone="America/Denver",
            ),
            {
                "object": "TimeSeriesFetchResult",
                "uuid": "4019e231-4f41-445c-9499-149d59d64dc5",
                "data_series": {
                    "2019-01-01T00:00:00Z": -14.3890757468198,
                    "2019-01-01T01:00:00Z": -6.57728772551002,
                    "2019-01-01T02:00:00Z": 2.77139392215585,
                    "2019-01-01T03:00:00Z": 12.4580712230353,
                },
                "create_time": "2019-01-01T00:00:05Z",
                "update_time": None,
            },
        )

        self.assertEqual(
            responses.mock.calls[4].request.url,
            (
                "https://api.myst.ai/v1alpha1/time_series/7e7de7a2-3de3-45e5-bf94-40374a0f8d14:fetch?"
                "start_time=2019-01-01T00%3A00%3A00Z&end_time=2019-01-01T03%3A00%3A00Z&time_zone=America%2FDenver"
            ),
        )

    @responses.activate
    def test_time_series_fetch_data_series(self):
        # Mock response
        responses.add(
            responses.GET,
            "https://api.myst.ai/v1alpha1/time_series/7e7de7a2-3de3-45e5-bf94-40374a0f8d14:fetch",
            json=self._EXAMPLE_FETCH_RESULT,
        )

        # Generate an example resource to test with.
        time_series = self._generate_resource(uuid="7e7de7a2-3de3-45e5-bf94-40374a0f8d14")
        self.assertEqual(
            time_series.fetch_data_series(
                start_time=pytz.utc.localize(datetime.datetime(2019, 1, 1)),
                end_time=pytz.utc.localize(datetime.datetime(2019, 1, 1, 3)),
            ),
            {
                "2019-01-01T00:00:00Z": -14.3890757468198,
                "2019-01-01T01:00:00Z": -6.57728772551002,
                "2019-01-01T02:00:00Z": 2.77139392215585,
                "2019-01-01T03:00:00Z": 12.4580712230353,
            },
        )
