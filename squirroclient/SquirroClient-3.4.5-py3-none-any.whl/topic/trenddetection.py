import json
from datetime import datetime, timedelta

from ..util import deprecation


class TrendDetectionMixin(object):
    def new_trenddetection(
        self,
        project_id,
        name,
        query,
        email_user,
        aggregation_interval,
        aggregation_field=None,
        aggregation_method=None,
        aggregation_time_field=None,
    ):
        """Create a new trend detection.

        :param project_id: Id of the project.
        :param query: Trend Detection query.
        :param name: The name of the new Trend Detection Entity.
        :param email_user: Email address for alert emails.
        :param aggregation_interval: Time aggregation interval for items.
            `aggregation_interval` is `{offset}{unit}` where `offset` is a
            number and `unit` is one of `m` (minutes), `h` (hours), `d` (days),
            `w` (weeks). Examples: `5m` for five minutes or `1d` for one day.

            This parameter defines the discretization level of the time series
            data for Trend Detection Analysis. As an example, setting this
            parameter to one week will result in the aggregation of data into
            one week windows for Trend Detection Analysis.
        :param aggregation_field: A numerical keyword field name to use
            as the base for trend detection
        :param aggregation_method: An aggregation method. Current options are
            'sum', 'avg', 'max' and 'min'. Defaults to 'avg'. Only used if
            aggregation_field is set too.
        :param aggregation_time_field: A datetime keyword field that is used
            as the timestamp for setting up trend detection instead. Defaults
            to `$item_created_at`.

        Example::

            >>> client.new_trenddetection(
                    project_id='2sic33jZTi-ifflvQAVcfw',
                    query='hello world',
                    name='test name',
                    email_user='test@squirro.com',
                    aggregation_interval='1w',
                    aggregation_field='votes',
                    aggregation_method='avg',
                    aggregation_time_field='my_datetime_facet'
                )
            {
                'trend_detection_entity': {
                    u'id': u'iR81vxDnShu5di4snCu6Jg',
                    u'created_at': u'2016-02-23T16:28:00',
                    u'modified_at': u'2016-02-23T16:28:00',
                    u'name': u'test name',
                    u'project_id': u'2sic33jZTi-ifflvQAVcfw',
                    u'query': u'hello world'
                    u'aggregation_interval': u'1w',
                    u'aggregation_field': u'votes',
                    u'aggregation_method': u'avg',
                    u'aggregation_time_field': u'my_datetime_facet',
                    u'email_user': u'test@squirro.com',
                    u'last_alert_timestamp': None,
                    u'last_seen_timestamp': None,
                    u'trends_healthy': None
                }
            }
        """
        url = self._get_trenddetection_base_url() % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        data = {
            "query": query,
            "name": name,
            "email_user": email_user,
            "aggregation_interval": aggregation_interval,
            "aggregation_field": aggregation_field,
            "aggregation_method": aggregation_method,
            "aggregation_time_field": aggregation_time_field,
        }

        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def modify_trenddetection(self, project_id, trenddetection_id, **kwargs):
        """
        Modifies a Trend detection Entity.

        :param project_id: Id of the project.
        :param trenddetection_id: Id of the trend detection entity.
        :param kwargs: Attributes of the tde to be updated. Update of only
            `name` and `email_user` attributes is supported.

        Example::

            >>> client.modify_trenddetection(
                project_id='2sic33jZTi-ifflvQAVcfw',
                tde_id='F3k1dEJEQzmLRaIlN71AsA',
                name='test_name', email_user='test@squirro.com')
        """

        # Get rid of `None` parameters
        params = dict([(k, v) for k, v in kwargs.items() if v is not None])

        url = self._get_trenddetection_base_url(trenddetection_id) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "trenddetection_id": trenddetection_id,
        }
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        res = self._perform_request(
            "put", url, data=json.dumps(params), headers=headers
        )
        return self._process_response(res, [204])

    def get_trenddetections(self, project_id):
        """Get details of all the trend detections on a particular project.

        :param project_id: Id of the project.
        :returns: A dictionary with all the Trend Detection Entities.

        Example::

            >>> client.get_trenddetections(project_id='2sic33jZTi-ifflvQAVcfw')
                {
                    u'trend_detection_entities': [
                        {
                            u'created_at': '2016-02-09T08:34:17',
                            u'id': 'nwBnJ5tkQVGMjKFUBZ1Cbw',
                            u'modified_at': '2016-02-09T08:34:19',
                            u'name': 'test_tde',
                            u'project_id': 'oFFPR28pTUOkmUF8pZO0cA',
                            u'query': '',
                            u'aggregation_interval': u'1w',
                            u'aggregation_field': u'votes',
                            u'aggregation_method': u'avg',
                            u'aggregation_time_field': u'my_datetime_facet'
                        }
                    ]
                }
        """
        url = self._get_trenddetection_base_url() % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Accept": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_trenddetection(
        self,
        project_id,
        trenddetection_id,
        include_trend_detection_entity=None,
        include_thresholds=None,
        include_anomalies=None,
        include_predictions=None,
        result_before=None,
        result_after=None,
    ):
        """Get details for a particular trend detection entity.

        :param project_id: Id of the project.
        :param trenddetection_id: Trend Detection identifier.
        :param include_trend_detection_entity: Boolean flag to include the
            trend detection entity parameters in the response. Defaults to
            `True` if not specified.
        :param include_thresholds: Boolean flag to include the thresholds
            corresponding of the trend detection entity in the response.
            Defaults to `False` if not specified.
        :param include_anomalies: Boolean flag to include the detected
            anomalies of the trend detection entity in the response. Defaults
            to `False` if not specified.
        :param include_predictions: Boolean flag to include the predictions and
            the corresponding threholds of the trend detection entity.
            Defaults to `False` if not specified.
        :param result_before: A Datetime type string to limit the time series
            data returned to be strictly before the `result_before` timestamp.
            If not specified, defaults to no end date restrictions for the
            returned data.
        :param result_after: A Datetime type string to limit the time series
            data returned to be strictly after the `result_after` timestamp.
            If not specified, defaults to no start date restrictions for the
            returned data.
        :returns: A dictionary with the requested Trend Detection Entity and
            various data-attributes based on the boolean flags.

        Example::

            >>> client.get_trenddetection(
            ...     project_id='oFFPR28pTUOkmUF8pZO0cA',
            ...     trenddetection_id='nwBnJ5tkQVGMjKFUBZ1Cbw',
            ...     include_trend_detection_entity=True,
            ...     include_thresholds=False,
            ...     include_anomalies=False,
            ...     include_predictions=False)
            {
                'trend_detection_entity': {
                    u'created_at': u'2016-02-09T08:34:17',
                    u'id': u'nwBnJ5tkQVGMjKFUBZ1Cbw',
                    u'modified_at': u'2016-02-09T08:34:19',
                    u'trends_healthy': True,
                    u'name': u'test name',
                    u'project_id': u'oFFPR28pTUOkmUF8pZO0cA',
                    u'query': u'test_query',
                    u'aggregation_interval': u'1w',
                    u'aggregation_field': u'votes',
                    u'aggregation_method': u'avg',
                    u'aggregation_time_field': u'my_datetime_facet'
                }
            }
        """
        # TODO: `include_historical_data` once we start storing historical data
        # also
        # prepare url
        url = self._get_trenddetection_base_url(trenddetection_id) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "trenddetection_id": trenddetection_id,
        }

        # prepare params
        params = {
            "include_trend_detection_entity": include_trend_detection_entity,
            "include_thresholds": include_thresholds,
            "include_anomalies": include_anomalies,
            "include_predictions": include_predictions,
            "result_after": result_after,
            "result_before": result_before,
        }

        params = dict([(k, v) for k, v in params.items() if v is not None])

        headers = {"Accept": "application/json"}
        res = self._perform_request("get", url, params=params, headers=headers)
        return self._process_response(res)

    def delete_trenddetection(self, project_id, trenddetection_id):
        """Delete a particular Trend Detection Entity.

        :param project_id: Id of the project.
        :param trenddetection_id: Trend detection identifier.

        Example::

            >>> client.delete_trenddetection(
            ...     project_id='2sic33jZTi-ifflvQAVcfw',
            ...     trenddetection_id='fd5x9NIqQbyBmF4Yph9MMw')
        """
        url = self._get_trenddetection_base_url(trenddetection_id) % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "trenddetection_id": trenddetection_id,
        }
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    # TODO: deprecate this method in lieu of `get_trenddetection` method. Also,
    # be aware of the difference in defaults of `get_trenddetection` method as
    # compared to `get_trenddetection_result` method.
    def get_trenddetection_result(
        self,
        project_id,
        trenddetection_id,
        result_before=None,
        result_after=None,
        include_thresholds=True,
        include_anomalies=True,
        include_historical_data=True,
        include_trend_detection_entity=True,
        include_predictions=False,
    ):
        """
        DEPRECATED. Please use the `get_trenddetection` method instead.

        Mostly a wrapper around `get_trenddetection` method to maintain
        backwards compatibility. Will be deprecated with the next release.
        Please use the `get_trenddetection` method.
        Returns predictions, anomalies, thresholds and the underlying data
        values of a trend detection entity.

        :param project_id: Id of the project
        :param trenddetection_id: Id of the trend detection entity
        :param result_before: Timestamp to determine the last time bucket to
            be fetched for trend-results
        :param result_after: Timestamp to determine the first time bucket to be
            fetched for trend-results
        :param include_thresholds: Flag to determine whether to include
            thresholds or not, defaults to True
        :param include_anomalies: Flag to determine whether to include
            anomalies or not, defaults to True
        :param include_historical_data: Flag to determine whether to include
            historical data or not, defaults to True
        :param include_trend_detection_entity: Flag to determine whether to
            include the trend-detection entity or not, defaults to True
        :param include_predictions: Flag to determine whether to include
            predictions or not, defaults to False

        :return: A dict of the trend detection entity, its underlying data
            values, its calculated threshold, anomalies and predictions.

        Example::

            >>> client.get_trenddetection_result(
            ...     project_id='2sic33jZTi-ifflvQAVcfw',
            ...     trenddetection_id='fd5x9NIqQbyBmF4Yph9MMw',
            ...     include_predictions=True)

                {
                    'thresholds': [
                        {u'count': 18.709624304,
                         u'timestamp': u'2016-01-25T00:00:00'},
                        {u'count': 17.6339240561,
                         u'timestamp': u'2016-02-01T00:00:00'},
                        {u'count': 16.6033921677,
                         u'timestamp': u'2016-02-08T00:00:00'},
                        {u'count': 17.5181532055,
                         u'timestamp': u'2016-02-15T00:00:00'}
                    ],
                    'historical_values': {
                        u'values': [
                            {u'value': 18, u'key': u'2016-01-25T00:00:00'},
                            {u'value': 5, u'key': u'2016-02-01T00:00:00'},
                            {u'value': 7, u'key': u'2016-02-08T00:00:00'},
                            {u'value': 4, u'key': u'2016-02-15T00:00:00'}],
                        u'interval_seconds': 604800.0,
                        u'interval_logical': False},
                     'trend_detection_entity': {
                        u'aggregation_time_field': u'$item_created_at',
                        u'aggregation_field': None,
                        u'name': u'test_client',
                        u'created_at': u'2016-05-04T09:03:55',
                        u'modified_at': u'2016-05-04T09:03:58',
                        u'aggregation_interval': u'1w',
                        u'aggregation_method': None,
                        u'query': u'',
                        u'project_id': u'ZjI9KK3zRTaMkYSzUL6Ehw',
                        u'id': u'lsXDwwErQkq7dGKDaRopQQ'
                    },
                    'anomalies': [u'2016-01-25T00:00:00'],
                    'predictions': [
                        {
                            u'timestamp': u'2016-02-22T00:00:00',
                            u'prediction_value': 8.3735121811,
                            u'prediction_threshold': 11.5988725339
                        },
                        {
                            u'timestamp': u'2016-02-29T00:00:00',
                            u'prediction_value': 11.8071893366,
                            u'prediction_threshold': 13.011517576
                        },
                        {
                            u'timestamp': u'2016-03-07T00:00:00',
                            u'prediction_value': 6.4798976922,
                            u'prediction_threshold': 11.8167726387
                        }
                    ]
                }
        """
        deprecation(
            "This method will be removed with release 2.5.3. Please use the "
            "`get_trenddetection` method instead."
        )

        # UTC -- time format
        # TODO: Remove this hardcoded time-format once the trends-service start
        # storing the historical data also as this will not be needed anymore
        time_format = "%Y-%m-%dT%H:%M:%S"

        # get trend-detection and all it's relevant parameters except the
        # historical data
        include_thresholds_for_historical_data = True
        include_tde_for_historical_data = True
        ret = self.get_trenddetection(
            project_id,
            trenddetection_id,
            include_tde_for_historical_data,
            include_thresholds_for_historical_data,
            include_anomalies,
            include_predictions,
            result_before,
            result_after,
        )

        # TODO: remove the logic for getting the historical data once the
        # trends-service store the historical data itself
        # get first & last timestamp of thresholds data, in order to filter the
        # historical data with the same time stamps
        if include_historical_data:

            # return empty historical data if we get back no thresholds data
            if len(ret["thresholds"]) < 2:
                ret["historical_values"] = {"values": []}

            else:
                interval = (
                    datetime.strptime(
                        ret["thresholds"][1].get("timestamp"), time_format
                    )
                    - datetime.strptime(
                        ret["thresholds"][0].get("timestamp"), time_format
                    )
                ).total_seconds()

                historical_data_first_bucket = ret["thresholds"][0].get("timestamp")
                historical_data_last_bucket = datetime.strptime(
                    ret["thresholds"][-1].get("timestamp"), time_format
                ) + timedelta(seconds=interval - 1)
                historical_data_last_bucket = historical_data_last_bucket.strftime(
                    time_format
                )

                # prepare params for fetching historical data
                time_field = ret["trend_detection_entity"].get("aggregation_time_field")
                if not time_field:
                    time_field = "$item_created_at"

                aggregation = {
                    "trend_detection_values": {
                        "fields": [time_field],
                        "interval": ret["trend_detection_entity"].get(
                            "aggregation_interval"
                        ),
                        "method": "histogram",
                        "min_doc_count": 0,
                    }
                }

                aggregation_field = ret["trend_detection_entity"].get(
                    "aggregation_field"
                )
                aggregation_method = ret["trend_detection_entity"].get(
                    "aggregation_method"
                )
                if aggregation_field and aggregation_method:
                    innerAggregation = {
                        "fields": [aggregation_field],
                        "method": aggregation_method,
                    }
                    aggregation["trend_detection_values"][
                        "aggregation"
                    ] = innerAggregation

                # query
                aggs = self.query(
                    project_id,
                    query=ret["trend_detection_entity"].get("query"),
                    aggregations=aggregation,
                    count=0,
                    created_before=historical_data_last_bucket,
                    created_after=historical_data_first_bucket,
                )
                aggs = aggs.get("aggregations", {})

                tds_aggs = aggs.get("trend_detection_values", {}).get(time_field)
                ret["historical_values"] = tds_aggs

                if not tds_aggs:
                    raise ValueError(
                        "Could not retrieve trend detection historical values"
                    )

        # remove thresholds and tde parameters if not requested originally
        if not include_thresholds:
            del ret["thresholds"]

        if not include_trend_detection_entity:
            del ret["trend_detection_entity"]

        return ret

    def _get_trenddetection_base_url(self, trenddetection_id=None):
        """Returns the URL template for a trend detection. """
        parts = ["%(ep)s/v0/%(tenant)s"]
        parts.append("/projects/%(project_id)s/trenddetections")

        if trenddetection_id:
            parts.append("/%(trenddetection_id)s")

        return "".join(parts)
