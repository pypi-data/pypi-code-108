# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Formats entities

    See: http://help.isogeo.com/api/complete/index.html

    NOTE: `format` being the name of a Python built-in function \
        (see: https://docs.python.org/3/library/functions.html#format), \
        we use the `frmt` shorter as replacement.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.enums import MetadataTypes
from isogeo_pysdk.models import Format
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
class ApiFormat:
    """Routes as methods of Isogeo API used to manipulate formats."""

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
        super(ApiFormat, self).__init__()

    @ApiDecorators._check_bearer_validity
    def listing(self, data_type: str = None, caching: bool = 1) -> list:
        """List formats available in Isogeo API.

        :param str data_type: type of metadata to filter on
        :param bool caching: option to cache the response

        :returns: list of dicts
        :rtype: list

        :Example:
        >>> formats = isogeo.formats.listing()
        >>> # count all formats
        >>> print(len(formats))
        32
        >>> # count formats which are only for vector dataset
        >>> print(len(isogeo.formats.listing(data_type="vector-dataset")))
        21
        >>> # list all unique codes
        >>> formats_codes = [i.get("code") for i in formats]
        >>> pprint.pprint(formats_codes)
        [
            'apic',
            'arcsde',
            'dgn',
            'dwg',
            'dxf',
            ...
        ]
        """
        # URL
        if data_type:
            if MetadataTypes.has_value(data_type):
                url_formats = utils.get_request_base_url(
                    route="formats/{}".format(data_type)
                )
                logger.debug(
                    "Listing available geographic formats for {} metadata...".format(
                        data_type
                    )
                )
            else:
                raise ValueError(
                    "Metadata type name '{}' is not one of accepted values: {}".format(
                        data_type, " | ".join(i.value for i in MetadataTypes)
                    )
                )
        else:
            url_formats = utils.get_request_base_url(route="formats/")
            logger.debug("Listing all available geographic formats...")

        # request
        req_formats = self.api_client.get(
            url=url_formats,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_formats)
        if isinstance(req_check, tuple):
            return req_check

        # cache
        if caching:
            self.api_client._formats_geo = req_formats.json()

        # end of method
        return req_formats.json()

    @ApiDecorators._check_bearer_validity
    def get(self, format_code: str) -> Format:
        """Get details about a specific format.

        :param str format_code: format code

        :rtype: Format

        :Example:
        >>> pprint.pprint(isogeo.formats.get("postgis"))
        {
            '_id': string (uuid),
            '_tag': 'format:postgis',
            'aliases': [],
            'code': 'postgis',
            'name': 'PostGIS',
            'type': 'dataset',
            'versions': [
                '2.2',
                '2.1',
                '2.0',
                '1.5',
                '1.4',
                '1.3',
                '1.2',
                '1.1',
                '1.0',
                '0.9',
                None
                ]
        }
        """

        # format route
        url_format = utils.get_request_base_url(route="formats/{}".format(format_code))

        # request
        req_format = self.api_client.get(
            url=url_format,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_format)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Format(**req_format.json())

    @ApiDecorators._check_bearer_validity
    def create(self, frmt: Format, check_exists: bool = 1) -> Format:
        """Add a new format to the Isogeo formats database.

        If a format with the same code already exists, the Isogeo API returns a 500 HTTP code.
        To prevent this error, use the check_exists option or check by yourself before.

        :param Format frmt: Format model object to create
        :param bool check_exists: check if a format with the same code exists before

        :rtype: Format or tuple

        :Example:

        .. code-block:: python

            format_to_add = Format(
                code="geojson",
                name="GeoJSON",
                type="vectorDataset"
            )
            isogeo.formats.create(format_to_add)
        """
        # check format code
        if not frmt.code:
            raise ValueError("Format code is required: {}".format(frmt.code))
        else:
            pass

        # check if format code doesn't exist
        if check_exists:
            # use cache if possible to retrive formats codes
            if self.api_client._formats_geo:
                formats_codes = [i.get("code") for i in self.api_client._formats_geo]
            else:
                formats_codes = [i.get("code") for i in self.listing()]
            # check if new code already exists
            if frmt.code in formats_codes:
                raise ValueError(
                    "Format code already exists: {}. Consider using 'format.update' instead.".format(
                        frmt.code
                    )
                )
        else:
            pass

        # URL
        url_format_create = utils.get_request_base_url(route="formats")

        # request
        req_new_format = self.api_client.post(
            url=url_format_create,
            json=frmt.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_new_format)
        if isinstance(req_check, tuple):
            return req_check

        # update cache
        self.api_client._formats_geo.append(req_new_format.json())

        # end of method
        return Format(**req_new_format.json())

    @ApiDecorators._check_bearer_validity
    def delete(self, frmt: Format):
        """Delete a format from Isogeo database.

        :param Format frmt: Format model object to delete
        """
        # URL
        url_format_delete = utils.get_request_base_url(
            route="formats/{}".format(frmt.code)
        )

        # request
        req_format_deletion = self.api_client.delete(
            url=url_format_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_format_deletion)
        if isinstance(req_check, tuple):
            return req_check

        # update cache
        self.listing()

        return req_format_deletion

    @ApiDecorators._check_bearer_validity
    def update(self, frmt: Format) -> Format:
        """Update a format in Isogeo database.

        :param Format frmt: Format model object to update

        :rtype: Format

        :Example:
        >>> # retrieve format to update
        >>> fmt_postgis = isogeo.formats.get("postgis")
        >>> # add new versions locally
        >>> fmt_postgis.versions.extend(["3.0", "3.1"])
        >>> # update online
        >>> fmt_postgis_updted = isogeo.formats.update(fmt_postgis)
        """
        # check format UUID
        if not checker.check_is_uuid(frmt._id):
            raise ValueError("Format ID is not a correct UUID: {}".format(frmt._id))
        else:
            pass
        # check format required code
        if not frmt.code:
            raise ValueError("Format code is required")
        else:
            pass

        # URL
        url_format_update = utils.get_request_base_url(
            route="formats/{}".format(frmt.code)
        )

        # request
        req_format_update = self.api_client.put(
            url=url_format_update,
            json=frmt.to_dict(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_format_update)
        if isinstance(req_check, tuple):
            return req_check

        # update cache
        self.listing()

        # end of method
        return Format(**req_format_update.json())

    # -- Routes to manage the formats for non geographic dataset ------------------------------------
    @ApiDecorators._check_bearer_validity
    def nogeo_search(
        self, query: str = None, page_size: int = 10, offset: int = 0
    ) -> list:
        """Search within data formats available in Isogeo API for NON GEOGRAPHICAL DATA ONLY.

        :param str query: search terms. Equivalent of **q** parameter in Isogeo API.
        :param int page_size: limits the number of results. Useful to paginate results display. Default value: 10. Max value: 100.
        :param int offset: offset to start page size from a specific results index

        :returns: list of dicts
        :rtype: list

        :Example:
        >>> isogeo.formats.search(query="a", page_size=1, offset=0)
        [
            {
                'aliases': [],
                'name': 'Adobe PDF',
                'versions':
                [
                    '7',
                    '1.7',
                    None,
                    None
                ]
            }
        ]
        """
        # handling request parameters
        payload = {"q": query, "_limit": page_size, "_offset": offset}

        # URL
        url_formats_search_nogeo = utils.get_request_base_url(
            route="formats/resource/search"
        )

        # request
        req_formats_search_nogeo = self.api_client.get(
            url=url_formats_search_nogeo,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_formats_search_nogeo)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_formats_search_nogeo.json()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_format = ApiFormat()
