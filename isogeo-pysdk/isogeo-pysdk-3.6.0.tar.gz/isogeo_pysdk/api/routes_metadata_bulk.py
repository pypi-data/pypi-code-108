#! python3  # noqa E265

"""
    Isogeo API v1 - API Route for bulk update on resources (= Metadata)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import BulkReport, BulkRequest, Metadata
from isogeo_pysdk.utils import IsogeoUtils

# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
checker = IsogeoChecker()
utils = IsogeoUtils()


# #############################################################################
# ########## Classes ###############
# ##################################
class ApiBulk:
    """Routes as methods of Isogeo API used to mass edition of metadatas (resources).

    :Example:

    .. code-block:: python

        # retrieve objects to be associated
        catalog_1 = isogeo.catalog.get(
            workgroup_id={WORKGROUP_UUID},
            catalog_id={CATALOG_UUID_1},
        )

        catalog_2 = isogeo.catalog.get(
            workgroup_id={WORKGROUP_UUID},
            catalog_id={CATALOG_UUID_2},
        )

        keyword = isogeo.keyword.get(keyword_id={KEYWORD_UUID},)

        # along the script, prepare the bulk requests
        isogeo.metadata.bulk.prepare(
            metadatas=(
                {METADATA_UUID_1},
                {METADATA_UUID_2},
            ),
            action="add",
            target="catalogs",
            models=(catalog_1, catalog_2),
        )

        isogeo.metadata.bulk.prepare(
            metadatas=(
                {METADATA_UUID_1},

            ),
            action="add",
            target="keywords",
            models=(keyword,),
        )

        # send the one-shot request
        isogeo.metadata.bulk.send()

    """

    BULK_DATA = []

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

        # initialize
        super(ApiBulk, self).__init__()

    def prepare(
        self, metadatas: tuple, action: str, target: str, models: tuple
    ) -> BulkRequest:
        """Prepare requests to be sent later in one shot.

        :param tuple metadatas: tuple of metadatas UUIDs or Metadatas to be updated
        :param str action: type of action to perform on metadatas. See: :class:`~isogeo_pysdk.enums.bulk_actions`.
        :param str target: kind of object to add/delete/update to the metadatas. See: :class:`~isogeo_pysdk.enums.bulk_targets`.
        :param tuple models: tuple of objects to be associated with the metadatas.
        """
        # instanciate a new Bulk REquest object
        prepared_request = BulkRequest()

        # ensure lowercase
        prepared_request.action = action.lower()
        # prepared_request.target = target.lower()
        prepared_request.target = target

        # check metadatas uuid
        metadatas = list(metadatas)
        for i in metadatas:
            if isinstance(i, str) and not checker.check_is_uuid(i):
                logger.error("Not a correct UUID: {}".format(i))
                metadatas.remove(i)
            elif isinstance(i, Metadata) and not checker.check_is_uuid(i._id):
                logger.error(
                    "Metadata passed but with an incorrect UUID: {}".format(i._id)
                )
                metadatas.remove(i)
            elif isinstance(i, Metadata) and checker.check_is_uuid(i._id):
                logger.debug("Metadata passed, extracting the UUID: {}".format(i._id))
                metadatas.append(i._id)
                metadatas.remove(i)
            else:
                continue

        # add it to the prepared request query
        prepared_request.query = {"ids": metadatas}

        # check passed objects
        obj_type = models[0]
        if not all([isinstance(obj, type(obj_type)) for obj in models]):
            raise TypeError(
                "Models must contain an unique type of objects. First found: {}".format(
                    obj_type
                )
            )

        prepared_request.model = [obj.to_dict() for obj in models]

        # add it to be sent later
        self.BULK_DATA.append(prepared_request.to_dict())

        return prepared_request

    @ApiDecorators._check_bearer_validity
    def send(self) -> list:
        """Send prepared BULK_DATA to the `POST BULK resources/`.

        :rtype: List[BulkReport]
        """

        # build request url
        url_metadata_bulk = utils.get_request_base_url(route="resources")

        # request
        req_metadata_bulk = self.api_client.post(
            url=url_metadata_bulk,
            json=self.BULK_DATA,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            stream=True,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_metadata_bulk)
        if isinstance(req_check, tuple):
            return req_check

        # empty bulk data
        self.BULK_DATA.clear()

        return [BulkReport(**req) for req in req_metadata_bulk.json()]


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    sample_test = ApiBulk()
    print(sample_test)
