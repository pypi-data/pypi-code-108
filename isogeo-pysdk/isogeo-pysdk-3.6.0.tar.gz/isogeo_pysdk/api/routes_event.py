# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Events entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from datetime import datetime

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Event, Metadata
from isogeo_pysdk.utils import IsogeoUtils

# #############################################################################
# ########## Global #############
# ##################################

logger = logging.getLogger(__name__)
checker = IsogeoChecker()
utils = IsogeoUtils()


# #############################################################################
# ########## Classes ###############
# ##################################
class ApiEvent:
    """Routes as methods of Isogeo API used to manipulate events."""

    def __init__(self, api_client=None):
        if api_client is not None:
            self.api_client = api_client

        # store API client (Request [Oauthlib] Session) and pass it to the decorators
        self.api_client = api_client
        ApiDecorators.api_client = api_client

        # ensure platform and others params to request
        (
            self.platform,
            self.api_url,
            self.app_url,
            self.csw_url,
            self.mng_url,
            self.oc_url,
            self.ssl,
        ) = utils.set_base_url(self.api_client.platform)
        # initialize
        super(ApiEvent, self).__init__()

    @ApiDecorators._check_bearer_validity
    def listing(self, metadata: Metadata) -> list:
        """Get all events of a metadata.

        :param Metadata metadata: metadata (resource) to edit
        """
        # URL
        url_events = utils.get_request_base_url(
            route="resources/{}/events".format(metadata._id)
        )

        # request
        req_events = self.api_client.get(
            url=url_events,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_events)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_events.json()

    @ApiDecorators._check_bearer_validity
    def event(self, metadata_id: str, event_id: str) -> Event:
        """Get details about a specific event.

        :param str event_id: event UUID to get
        :param str event_id: event UUID
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata_id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata_id)
            )
        else:
            pass

        # check event UUID
        if not checker.check_is_uuid(event_id):
            raise ValueError("Event ID is not a correct UUID.")
        else:
            pass

        # URL
        url_event = utils.get_request_base_url(
            route="resources/{}/events/{}".format(metadata_id, event_id)
        )

        # request
        req_event = self.api_client.get(
            url=url_event,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_event)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        event_augmented = req_event.json()
        event_augmented["parent_resource"] = metadata_id

        # end of method
        return Event(**event_augmented)

    @ApiDecorators._check_bearer_validity
    def create(self, metadata: Metadata, event: Event) -> Event:
        """Add a new event to a metadata (= resource).

        :param Metadata metadata: metadata (resource) to edit
        :param Event Event: event object to create
        """
        # check params
        if event.kind not in ("creation", "update", "publication"):
            raise ValueError(
                "'event.kind' must be one of: creation, update, publication"
            )

        if isinstance(event.date, str):
            if len(event.date) == 10:
                # 2019-08-09
                datetime.strptime(event.date, "%Y-%m-%d")
            elif len(event.date) == 25:
                # ISO 8601 as returned by the API: '2019-08-09T00:00:00+00:00'
                datetime.strptime(event.date[:10], "%Y-%m-%dT%H:%M:%S")
            else:
                logger.warning("Unknown date format: {}".format(event.date))
        elif isinstance(event.date, datetime):
            event.date = event.date.strftime("%Y-%m-%d")
        else:
            raise TypeError("'event.date' must be a str or a datetime")

        # ensure that a creation date doesn't already exist
        if event.kind == "creation":
            # retrieve metadata events
            metadata_events = self.api_client.metadata.get(
                metadata._id, include=("events",)
            )
            # filter on creation events
            events_creation = [
                event for evt in metadata_events.events if evt.get("kind") == "creation"
            ]
            if events_creation:
                logger.warning(
                    "A creation event already exist. A metadata can only have one creation event. Use event_update instead."
                )
                return events_creation[0]

        # ensure removing event.description for creation dates
        if event.kind == "creation" and event.description:
            event.description = None
            logger.warning("Event comments are not allowed for creation dates")

        # URL
        url_event_create = utils.get_request_base_url(
            route="resources/{}/events".format(metadata._id)
        )

        # request
        req_new_event = self.api_client.post(
            url=url_event_create,
            json={
                "date": event.date,
                "description": event.description,
                "kind": event.kind,
            },
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_event)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        event_augmented = req_new_event.json()
        event_augmented["parent_resource"] = metadata._id

        # end of method
        return Event(**event_augmented)

    @ApiDecorators._check_bearer_validity
    def delete(self, event: Event, metadata: Metadata = None):
        """Delete a event from Isogeo database.

        :param class event: Event model object to delete
        :param Metadata metadata: parent metadata (resource) containing the event
        """
        # check event UUID
        if not checker.check_is_uuid(event._id):
            raise ValueError("Event ID is not a correct UUID: {}".format(event._id))
        else:
            pass

        # retrieve parent metadata
        if not checker.check_is_uuid(event.parent_resource) and not metadata:
            raise ValueError("Event parent metadata is required. Requesting it...")
        elif not checker.check_is_uuid(event.parent_resource) and metadata:
            event.parent_resource = metadata._id
        else:
            pass

        # URL
        url_event_delete = utils.get_request_base_url(
            route="resources/{}/events/{}".format(event.parent_resource, event._id)
        )

        # request
        req_event_deletion = self.api_client.delete(
            url=url_event_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_event_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_event_deletion

    @ApiDecorators._check_bearer_validity
    def update(self, event: Event, metadata: Metadata = None) -> Event:
        """Update an event.

        :param class event: Event model object to update
        :param Metadata metadata: parent metadata (resource) containing the event
        """
        # check event UUID
        if not checker.check_is_uuid(event._id):
            raise ValueError("Event ID is not a correct UUID: {}".format(event._id))
        else:
            pass

        # retrieve parent metadata
        if not checker.check_is_uuid(event.parent_resource) and not metadata:
            raise ValueError("Event parent metadata is required. Requesting it...")
        elif not checker.check_is_uuid(event.parent_resource) and metadata:
            event.parent_resource = metadata._id
        else:
            pass

        # URL
        url_event_update = utils.get_request_base_url(
            route="resources/{}/events/{}".format(event.parent_resource, event._id)
        )

        # request
        req_event_update = self.api_client.put(
            url=url_event_update,
            json=event.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_event_update)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        event_augmented = req_event_update.json()
        event_augmented["parent_resource"] = event.parent_resource

        # end of method
        return Event(**event_augmented)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_event = ApiEvent()
