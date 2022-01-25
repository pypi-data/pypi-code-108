#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Resources (= Metadata) entity

    See: http://help.isogeo.com/api/complete/index.html#definition-resource
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from functools import lru_cache

# 3rd party
from requests.models import Response

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Metadata
from isogeo_pysdk.utils import IsogeoUtils

# other routes
from .routes_event import ApiEvent
from .routes_metadata_bulk import ApiBulk
from .routes_condition import ApiCondition
from .routes_conformity import ApiConformity
from .routes_feature_attributes import ApiFeatureAttribute
from .routes_limitation import ApiLimitation
from .routes_link import ApiLink
from .routes_service_layers import ApiServiceLayer
from .routes_service_operations import ApiServiceOperation

# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
checker = IsogeoChecker()
utils = IsogeoUtils()


# #############################################################################
# ########## Classes ###############
# ##################################
class ApiMetadata:
    """Routes as methods of Isogeo API used to manipulate metadatas (resources)."""

    def __init__(self, api_client=None):
        if api_client is not None:
            self.api_client = api_client

        # store API client (Request [Oauthlib] Session) and pass it to the decorators
        self.api_client = api_client
        ApiDecorators.api_client = api_client

        # ensure platform to request
        (
            self.platform,
            self.api_url,
            self.app_url,
            self.csw_url,
            self.mng_url,
            self.oc_url,
            self.ssl,
        ) = utils.set_base_url(self.api_client.platform)

        # sub routes
        self.attributes = ApiFeatureAttribute(self.api_client)
        self.bulk = ApiBulk(self.api_client)
        self.conditions = ApiCondition(self.api_client)
        self.conformity = ApiConformity(self.api_client)
        self.events = ApiEvent(self.api_client)
        self.layers = ApiServiceLayer(self.api_client)
        self.limitations = ApiLimitation(self.api_client)
        self.links = ApiLink(self.api_client)
        self.operations = ApiServiceOperation(self.api_client)

        # initialize
        super(ApiMetadata, self).__init__()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def get(self, metadata_id: str, include: tuple or str = ()) -> Metadata:
        """Get complete or partial metadata about a specific metadata (= resource).

        :param str metadata_id: metadata UUID to get
        :param tuple include: subresources that should be included. Available values:

          - one or various from MetadataSubresources (Enum)
          - "all" to get complete metadata with every subresource included
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata_id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata_id)
            )
        else:
            pass

        # request parameters
        payload = {
            "_include": checker._check_filter_includes(
                includes=include, entity="metadata"
            )
        }

        # URL
        url_resource = utils.get_request_base_url(
            route="resources/{}".format(metadata_id)
        )

        # request
        req_metadata = self.api_client.get(
            url=url_resource,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_metadata)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Metadata.clean_attributes(req_metadata.json())

    @ApiDecorators._check_bearer_validity
    def create(
        self, workgroup_id: str, metadata: Metadata, return_basic_or_complete: int = 0
    ) -> Metadata:
        """Add a new metadata to a workgroup.

        :param str workgroup_id: identifier of the owner workgroup
        :param Metadata metadata: Metadata model object to create
        :param int return_basic_or_complete: creation of metada uses a bulk script.\
          So, by default API does not return the complete object but the minimal info.\
          This option allow to overrides the basic behavior. Options:

          - 0 = dry (only the _id, title and attributes passed for the creation) [DEFAULT]
          - 1 = basic without any include (requires an additionnal request)
          - 2 = complete with all include (requires an additionnal request)

        :rtype: Metadata

        :Example:

        .. code-block:: python

            # create a local metadata
            my_metadata = Metadata(
                title="My awesome metadata",    # required
                type="vectorDataset",           # required
                abstract="Here comes my **awesome** description with a piece of markdown."  # optional
            )

            # push it online
            isogeo.metadata.create(
                workgroup_id=WORKGROUP_UUID,
                metadata=my_metadata
            )
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError("Workgroup ID is not a correct UUID.")
        else:
            pass

        # check required attributes
        if not metadata.title:
            raise ValueError("Metadata title is required: {}".format(metadata.title))
        else:
            pass
        if not metadata.type:
            logger.warning(
                "Metadata type is not specified, so the 'resource' type will be applied"
            )
        else:
            pass

        # build request url
        url_metadata_create = utils.get_request_base_url(
            route="groups/{}/resources".format(workgroup_id)
        )

        # request
        req_new_metadata = self.api_client.post(
            url=url_metadata_create,
            json=metadata.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_metadata)
        if isinstance(req_check, tuple):
            return req_check

        # load new metadata
        resp_md = req_new_metadata.json()
        resp_md["_creator"] = {"_id": workgroup_id}
        new_metadata = Metadata(**resp_md)

        # return basic metadata or complete
        if return_basic_or_complete == 1:
            return self.get(metadata_id=new_metadata._id)
        elif return_basic_or_complete == 2:
            return self.get(metadata_id=new_metadata._id, include="all")
        else:
            return new_metadata

    @ApiDecorators._check_bearer_validity
    def delete(self, metadata_id: str) -> Response:
        """Delete a metadata from Isogeo database.

        :param str metadata_id: identifier of the resource to delete
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata_id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata_id)
            )
        else:
            pass

        # request URL
        url_metadata_delete = utils.get_request_base_url(
            route="resources/{}".format(metadata_id)
        )

        # request
        req_metadata_deletion = self.api_client.delete(
            url_metadata_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_metadata_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_metadata_deletion

    @ApiDecorators._check_bearer_validity
    def exists(self, resource_id: str) -> bool:
        """Check if the specified resource exists and is available for the authenticated user.

        :param str resource_id: identifier of the resource to verify
        """
        # check metadata UUID
        if not checker.check_is_uuid(resource_id):
            raise ValueError(
                "Resource ID is not a correct UUID: {}".format(resource_id)
            )
        else:
            pass

        # request URL
        url_metadata_exists = utils.get_request_base_url(
            route="resources/{}".format(resource_id)
        )

        # request
        req_metadata_exists = self.api_client.get(
            url=url_metadata_exists,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_metadata_exists)
        if isinstance(req_check, tuple):
            return False

        return True

    @ApiDecorators._check_bearer_validity
    def update(self, metadata: Metadata, _http_method: str = "PATCH") -> Metadata:
        """Update a metadata, but **ONLY** the root attributes, not the subresources.

        Certain attributes of the Metadata object to update are required:

          - _id
          - editionProfile
          - type

        See: https://github.com/isogeo/isogeo-api-py-minsdk/issues/116

        :param Metadata metadata: metadata object to update
        :param str _http_method: HTTP method (verb) to use. \
            Default to 'PATCH' but can be set to 'PUT' in certain cases (services).

        :rtype: Metadata
        :returns: the updated metadata or the request error.

        :Example:

        .. code-block:: python

            # get a metadata
            my_metadata = isogeo.metadata.get(metadata_id=METADATA_UUID)
            # add an updated watermark in the abstract
            my_metadata.abstract += '**Updated!**'
            # push it online
            isogeo.metadata.update(my_metadata)

        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # check metadata required type
        if not metadata.type:
            raise ValueError("Metadata type is required: {}".format(metadata.type))
        else:
            pass

        # check metadata required editionProfile
        if not metadata.editionProfile:
            logger.warning(
                "Metadata to update is missing a required attribute 'editionProfile'. "
                "It'll be set to 'manual'."
                "See: https://github.com/isogeo/isogeo-api-py-minsdk/issues/116."
            )
            metadata.editionProfile = "manual"
        else:
            pass

        # URL builder
        url_metadata_update = utils.get_request_base_url(
            route="resources/{}".format(metadata._id)
        )

        # HTTP method according to the metadata.type
        if metadata.type == "service" and _http_method != "PUT":
            return self.update(metadata=metadata, _http_method="PUT")

        # request
        req_metadata_update = self.api_client.request(
            method=_http_method,
            url=url_metadata_update,
            json=metadata.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_metadata_update)
        if isinstance(req_check, tuple):
            return req_check

        # return updated object
        return Metadata(**req_metadata_update.json())

    # -- Routes to manage the related objects ------------------------------------------
    @ApiDecorators._check_bearer_validity
    def download_xml(self, metadata: Metadata) -> Response:
        """Download the metadata exported into XML ISO 19139.

        :param Metadata metadata: metadata object to export

        :rtype: Response

        :Example:

        .. code-block:: python

            # get the download stream
            xml_stream = isogeo.metadata.download_xml(Metadata(_id=METADATA_UUID))
            # write it to a file
            with open("./{}.xml".format("metadata_exported_as_xml"), "wb") as fd:
                for block in xml_stream.iter_content(1024):
                    fd.write(block)
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # URL
        url_metadata_dl_xml = utils.get_request_base_url(
            route="resources/{}.xml".format(metadata._id)
        )

        # request
        req_metadata_dl_xml = self.api_client.get(
            url=url_metadata_dl_xml,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            stream=True,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_metadata_dl_xml)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_metadata_dl_xml

    # -- Routes to manage subresources -------------------------------------------------
    @lru_cache()
    def catalogs(self, metadata: Metadata) -> list:
        """Returns asssociated catalogs with a metadata. Just a shortcut.

        :param Metadata metadata: metadata object

        :rtype: list
        """
        return self.api_client.catalog.metadata(metadata_id=metadata._id)

    def keywords(
        self, metadata: Metadata, include: tuple = ("_abilities", "count", "thesaurus")
    ) -> list:
        """Returns asssociated keywords with a metadata. Just a shortcut.

        :param Metadata metadata: metadata object
        :param tuple include: subresources that should be returned. Available values:

        * '_abilities'
        * 'count'
        * 'thesaurus'

        :rtype: list
        """
        return self.api_client.keyword.metadata(
            metadata_id=metadata._id, include=include
        )


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_metadata = ApiMetadata()
    print(api_metadata)
