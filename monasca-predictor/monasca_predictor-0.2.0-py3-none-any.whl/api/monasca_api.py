"""
    Monasca API client
"""

import logging

from keystoneauth1.exceptions import base as keystoneauth_exception
from monascaclient import client
from monasca_agent.common import keystone
from osc_lib import exceptions

import monasca_predictor.common.util as util

log = logging.getLogger(__name__)


class MonascaAPI(object):
    """Interface to Monasca API."""

    DEFAULT_AGGREGATION_PERIOD_SECONDS = 300

    def __init__(self, config):
        """Initialize Monasca API client connection."""
        self._config = config
        self._mon_client = None
        self._api_version = "2_0"

        self._api_call_timeout = int(config["api_call_timeout"])
        self._failure_reason = None

    def get_measurements(
        self,
        metric,
        start_time,
        tenant,
        instance_id=None,
        dimensions=None,
        group_by=None,
        merge_metrics=None,
        statistics=None,
        aggregation_period_seconds=None,
    ):

        if not self._mon_client:
            self._mon_client = self._get_mon_client()
            if not self._mon_client:
                log.warning("Keystone API is down or unreachable")
                return None

        # NOTE: params name must match the one expected by Monasca API
        kwargs = {
            "dimensions": {},
            "name": metric,
            "start_time": start_time,
            "tenant_id": tenant,
            "merge_metrics": merge_metrics or False,
        }

        if instance_id:
            kwargs["dimensions"]["resource_id"] = instance_id

        if dimensions:
            kwargs["dimensions"].update(dimensions)

        if group_by:
            kwargs["group_by"] = group_by

        if statistics:
            kwargs["statistics"] = statistics
            kwargs["period"] = (
                aggregation_period_seconds
                or MonascaAPI.DEFAULT_AGGREGATION_PERIOD_SECONDS
            )

        log.debug(
            "Sending request to Monasca API with the following parameters:\n%s",
            util.format_object_str(kwargs),
        )

        try:
            if statistics:
                return self._mon_client.metrics.list_statistics(**kwargs)

            return self._mon_client.metrics.list_measurements(**kwargs)

        except exceptions.ClientException as ex:
            log.exception("ClientException: error sending message to monasca-api.")
            self._failure_reason = (
                f"Error sending message to the Monasca API: {str(ex)}"
            )

        except Exception:  # pylint: disable=broad-except
            log.exception("Error sending message to Monasca API.")
            self._failure_reason = "The Monasca API is DOWN or unreachable"

        return None

    def _get_mon_client(self):
        """Initialize Monasca API client instance with session."""
        try:
            keystone_client = keystone.Keystone(self._config)
            endpoint = keystone_client.get_monasca_url()
            session = keystone_client.get_session()
            monasca_client = client.Client(
                api_version=self._api_version,
                endpoint=endpoint,
                session=session,
                timeout=self._api_call_timeout,
                **keystone.get_args(self._config),
            )
            return monasca_client

        except keystoneauth_exception.ClientException as ex:
            log.error("Failed to initialize Monasca client. %s", ex)

        return None
