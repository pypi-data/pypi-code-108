# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes to manage metadata limitations.

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Limitation, Metadata
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
class ApiLimitation:
    """Routes as methods of Isogeo API used to manipulate metadata limitations (CGUs)."""

    def __init__(self, api_client=None):
        if api_client is not None:
            self.api_client = api_client

        # store API client (Request [oAuthlib] Session) and pass it to the decorators
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
        super(ApiLimitation, self).__init__()

    @ApiDecorators._check_bearer_validity
    def listing(self, metadata: Metadata) -> list:
        """Get limitations of a metadata.

        :param Metadata metadata: metadata (resource)
        """
        # request URL
        url_limitations = utils.get_request_base_url(
            route="resources/{}/limitations/".format(metadata._id)
        )

        # request
        req_limitations = self.api_client.get(
            url=url_limitations,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_limitations)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_limitations.json()

    @ApiDecorators._check_bearer_validity
    def get(self, metadata_id: str, limitation_id: str) -> Limitation:
        """Get details about a specific limitation.

        :param str metadata_id: metadata UUID
        :param str limitation_id: limitation UUID

        :Example:
        >>> # get a metadata
        >>> md = isogeo.metadata.get(METADATA_UUID)
        >>> # list its limitations
        >>> md_limitations = isogeo.metadata.limitations.listing(md)
        >>> # get the first limitation
        >>> limitation = isogeo.metadata.limitations.get(
            metadata_id=md._id,
            limitation_id=md_limitations[0].get("_id")
            )
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata_id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata_id)
            )
        else:
            pass

        # check limitation UUID
        if not checker.check_is_uuid(limitation_id):
            raise ValueError("Features Attribute ID is not a correct UUID.")
        else:
            pass

        # URL
        url_limitation = utils.get_request_base_url(
            route="resources/{}/limitations/{}".format(metadata_id, limitation_id)
        )

        # request
        req_limitation = self.api_client.get(
            url=url_limitation,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_limitation)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        limitation_augmented = req_limitation.json()
        limitation_augmented["parent_resource"] = metadata_id

        # end of method
        return Limitation(**limitation_augmented)

    @ApiDecorators._check_bearer_validity
    def create(self, metadata: Metadata, limitation: Limitation) -> Limitation:
        """Add a new limitation to a metadata (= resource).

        :param Metadata metadata: metadata (resource) to edit
        :param Limitation limitation: limitation object to create

        :returns: 409 if a limitation with the same name already exists.

        :rtype: Limitation or tuple

        :Example:

        .. code-block:: python

            # retrieve metadata
            md = isogeo.metadata.get(METADATA_UUID)
            # create the limitation locally
            new_limitation = Limitation(
                type="legal",
                restriction="patent",
                description="Do not use for commercial purpose.",
                )
            # add it to the metadata
            isogeo.metadata.limitations.create(md, new_limitation)
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # check relation between type and restriction/directive
        if limitation.type == "security":
            if limitation.restriction is not None:
                limitation.restriction = None
                logger.warning(
                    "Limitation restriction are not allowed for security limitations. Only description will be sent."
                )
            if limitation.directive is not None:
                limitation.directive = None
                logger.warning(
                    "Limitation directive are not allowed for security limitations. Only description will be sent."
                )

        # URL
        url_limitation_create = utils.get_request_base_url(
            route="resources/{}/limitations/".format(metadata._id)
        )

        # request
        req_new_limitation = self.api_client.post(
            url=url_limitation_create,
            json=limitation.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_limitation)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        limitation_augmented = req_new_limitation.json()
        limitation_augmented["parent_resource"] = metadata._id

        # end of method
        return Limitation(**limitation_augmented)

    @ApiDecorators._check_bearer_validity
    def delete(self, limitation: Limitation, metadata: Metadata = None):
        """Delete a limitation from a metadata.

        :param Limitation limitation: Limitation model object to delete
        :param Metadata metadata: parent metadata (resource) containing the limitation
        """
        # check limitation UUID
        if not checker.check_is_uuid(limitation._id):
            raise ValueError(
                "Limitation ID is not a correct UUID: {}".format(limitation._id)
            )
        else:
            pass

        # retrieve parent metadata
        if not checker.check_is_uuid(limitation.parent_resource) and not metadata:
            raise ValueError("Limitation parent metadata is required. Requesting it...")
        elif not checker.check_is_uuid(limitation.parent_resource) and metadata:
            limitation.parent_resource = metadata._id
        else:
            pass

        # URL
        url_limitation_delete = utils.get_request_base_url(
            route="resources/{}/limitations/{}".format(
                limitation.parent_resource, limitation._id
            )
        )

        # request
        req_limitation_deletion = self.api_client.delete(
            url=url_limitation_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_limitation_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_limitation_deletion

    @ApiDecorators._check_bearer_validity
    def update(self, limitation: Limitation, metadata: Metadata = None) -> Limitation:
        """Update a limitation.

        :param Limitation limitation: Limitation model object to update
        :param Metadata metadata: parent metadata (resource) containing the limitation
        """
        # check limitation UUID
        if not checker.check_is_uuid(limitation._id):
            raise ValueError(
                "Limitation ID is not a correct UUID: {}".format(limitation._id)
            )
        else:
            pass

        # retrieve parent metadata
        if not checker.check_is_uuid(limitation.parent_resource) and not metadata:
            raise ValueError("Limitation parent metadata is required. Requesting it...")
        elif not checker.check_is_uuid(limitation.parent_resource) and metadata:
            limitation.parent_resource = metadata._id
        else:
            pass

        # URL
        url_limitation_update = utils.get_request_base_url(
            route="resources/{}/limitations/{}".format(
                limitation.parent_resource, limitation._id
            )
        )

        # request
        req_limitation_update = self.api_client.put(
            url=url_limitation_update,
            json=limitation.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_limitation_update)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        limitation_augmented = req_limitation_update.json()
        limitation_augmented["parent_resource"] = limitation.parent_resource

        # end of method
        return Limitation(**limitation_augmented)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_directive = ApiLimitation()
