# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Metadata of Services (web geo services)

    See: http://help.isogeo.com/api/complete/index.html#definition-resource
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from urllib.parse import urlparse, parse_qs, urlunparse

# 3rd party
import requests

# submodules
from isogeo_pysdk.exceptions import AlreadyExistError
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Metadata
from isogeo_pysdk.utils import IsogeoUtils

# other routes
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
class ApiService:
    """Routes as methods of Isogeo API used to manipulate metadatas of web geo services (services).

    It's a set of helpers and shortcuts to make easier the sevrice management with the isogeo API.
    """

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
        self.layers = ApiServiceLayer(self.api_client)
        self.operations = ApiServiceOperation(self.api_client)

        # initialize
        super(ApiService, self).__init__()

    def create(
        self,
        workgroup_id: str,
        service_url: str,
        service_type: str = "guess",
        service_format: str = None,
        service_title: str = None,
        check_exists: bool = 1,
        ignore_avaibility: bool = 0,
        http_verb: str = "HEAD",
    ) -> Metadata:
        """Add a new metadata of a geographic webservice to a workgroup.

        It's just a helper to make it easy to create a metadata of a service with autofill for service layers.

        :param str workgroup_id: identifier of the owner workgroup
        :param str service_url: URL of the service
        :param str service_type: type of service. Must be one of: 'esri', 'esri_ogc', 'ogc', 'guess'
        :param str service_format: format of the web service. Must be one of the accepted codes in API (Non exhaustive list: 'efs', 'ems', 'wfs', 'wms', 'wmts'). If is None, so the it'll try to guess it from the URL.
        :param str service_title: title for the metadata service in case of analisis fail. OPTIONNAL.
        :param bool check_exists: check if a metadata with the same service base URL and format alerady exists. Defaults to True.
        :param bool ignore_avaibility: the service URL is tested to determine if it can be reached (HEAD then GET). This option allow to ignore the test result.\
            Can be useful if the service is only reachable by certains URLs or domains like *.isogeo.com. Defaults to False.
        :param str http_verb: HTTP verb to use to check the if the service is available. Must be one of: GET, HEAD

        :rtype: Service

        :raises ValueError: if workgroup_id is not a correct UUID | if http_verb or service_type is not a correct value
        :raises AlreadyExistError: if a metadata service with the same base URL already exists in the workgroup

        :Example:

        .. code-block:: python

            # for an OGC WMS by GeoServer, passing type and format
            isogeo.services.create(
                workgroup_id=WORKGROUP_UUID,
                service_type="ogc",
                service_format="wms",
                service_url="https://magosm.magellium.com/geoserver/ows?service=wms&version=1.3.0&request=GetCapabilities"
            )
            # for an OGC WFS by ArcGIS Server, passing only the service URL with query parameters
            new_srv = isogeo.services.create(
                workgroup_id=WORKGROUP_UUID,
                service_url="https://ligeo.paysdelaloire.fr/server/services/Le_Mans/Le_Mans_service/MapServer/WFSServer?request=GetCapabilities&service=WFS",
            )
            # for an Esri FeatureServer
            new_srv = isogeo.services.create(
                workgroup_id=WORKGROUP_UUID,
                service_url="https://api-carto.dijon.fr/arcgis/rest/services/SIGNALISATION/signalisation_MAJ/FeatureServer?f=pjson",
            )
        """
        # CHECKS PARAMS
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError("Workgroup ID is not a correct UUID.")
        else:
            pass

        # check http_verb
        http_verb = http_verb.upper()
        if http_verb not in ("GET", "HEAD"):
            raise ValueError(
                "HTTP VERB is not one of accepted valued: GET | HEAD. "
                "Furthermore it's recommended to leave the default value."
            )

        # check service type value
        service_type = service_type.lower()
        if service_type not in ("esri", "esri_ogc", "ogc", "guess"):
            raise ValueError(
                "Service type is not one of accepted valued: esri | esri_ogc | ogc | guess"
            )

        # check if service is available
        # do not use Isogeo Api client to make requests because of tokens, use a 'fresh' requests session
        # TO DO: improve http handler isogeo_adapter = HTTPAdapter(max_retries=3)
        req_check_reachable = requests.request(method=http_verb, url=service_url)
        if req_check_reachable.status_code >= 400 and http_verb == "HEAD":
            logger.debug(
                "HEAD failed. It can occur because of an Esri server... Retrying one again with a GET..."
            )
            return self.create(
                workgroup_id=workgroup_id,
                service_url=service_url,
                service_type=service_type,
                service_format=service_format,
                service_title=service_title,
                check_exists=check_exists,
                ignore_avaibility=ignore_avaibility,
                http_verb="GET",
            )
        elif req_check_reachable.status_code >= 400 and http_verb == "GET":
            if ignore_avaibility:
                logger.error(
                    "GET failed. Geographic server doesn't seem to be reachable but the avaibility is set to be ignored."
                )
            else:
                logger.warning(
                    "GET failed. Geographic server seems to be out of service"
                )
                return (False, req_check_reachable)
        else:
            logger.debug(
                "{} successed. Service {} is reachable.".format(http_verb, service_url)
            )
            pass

        # -- SERVICE URL
        url_parsed = urlparse(service_url)  # parsing the given URL
        # extracting the query string (after the '?') and lowering keys
        url_query = parse_qs(url_parsed.query)
        url_query = {k.lower(): v for k, v in url_query.items()}
        # get the base url cleaned
        url_clean = urlunparse(url_parsed._replace(query=None))
        logger.debug(
            "Service URL has been cleaned: {} from query parameters {}".format(
                url_clean, url_query
            )
        )

        # -- SERVICE TYPE
        if service_type == "guess":
            logger.debug(
                "Let's try to guess the service type from the URL path: {}".format(
                    url_parsed.path
                )
            )
            if "FeatureServer" in url_parsed.path:
                service_type = "esri"
            elif "MapServer" in url_clean and not (
                "WMSServer" in url_parsed.path or "WFSServer" in url_parsed.path
            ):
                service_type = "esri"
            else:
                service_type = "ogc"
                pass
            logger.debug("Service type guessed: {}".format(service_type))
        else:
            pass

        # -- SERVICE FORMAT
        # retrieve service format if it's not given
        if service_format is None:
            logger.debug("No format passed. Trying to extract one from the URL...")
            if service_type in ("esri_ogc", "ogc", "guess"):
                if not url_query:
                    raise ValueError(
                        "Service format can't be deduced without query parameters or specified format"
                    )
                elif "service" in set(k.lower() for k in url_query):
                    service_format = url_query.get("service")[0].lower()
                    logger.debug(
                        "Service format extracted from the query parameters: {}".format(
                            service_format
                        )
                    )
                else:
                    raise Exception(
                        "Service format passed was {} could not be extracted from URL query: {}".format(
                            service_format, url_query
                        )
                    )
            else:
                if "FeatureServer" in url_clean:
                    service_format = "efs"
                elif "MapServer" in url_clean:
                    service_format = "ems"
                pass
        else:
            # let's use the passed service format
            pass

        # retrive available formats for services within Isogeo API
        if len(self.api_client._formats_geo):  # using the cache if exists
            formats = self.api_client._formats_geo
        else:
            formats = self.api_client.formats.listing(data_type="service")
        srv_formats_codes = [
            i.get("code") for i in formats if i.get("type") == "service"
        ]

        # compare
        if service_format not in srv_formats_codes:
            raise Warning(
                "Service format '{}' is not an accepted one: {}".format(
                    service_format, " | ".join(srv_formats_codes)
                )
            )

        # -- SERVICE TITLE
        # check service title
        if service_title is None:
            service_title = "{} - {}".format(url_parsed.netloc, service_format)
            logger.warning(
                "No temporary title given but it's a required attribute to create metadata, "
                "so a generic one based on service URL is added: {}".format(
                    service_title
                )
            )
        else:
            pass

        # check if metadata already exists in workgroup
        # based on the format and base URL (cleaned)
        if check_exists:
            # retrieve workgroup metadatas
            md_services = self.api_client.search(
                query="type:service format:{} owner:{}".format(
                    service_format, workgroup_id
                ),
                page_size=100,
            )
            for md_service in md_services.results:
                if md_service.get("path") == url_clean:
                    msg_error = (
                        "Service metadata with the same base URL already exists: {} ({}). "
                        "Use 'update' instead or disable 'check_exists' option if you still "
                        "want to create duplicated service metadata.".format(
                            md_service.get("_id"), md_service.get("path")
                        )
                    )
                    logger.error(msg_error)
                    raise AlreadyExistError(msg_error)
        else:
            pass

        # -- CREATION
        # instanciate new service metadata locally
        new_metadata_service = Metadata(
            series=0,
            format=service_format,
            type="service",
            path=url_clean,
            title=service_title,
        )

        # checking response
        if isinstance(new_metadata_service, tuple):
            return new_metadata_service

        # create it online
        new_metadata_service = self.api_client.metadata.create(
            workgroup_id=workgroup_id, metadata=new_metadata_service
        )

        # update it (patch) to trigger the layers autofill
        self.api_client.metadata.update(new_metadata_service)

        new_md = self.api_client.metadata.get(
            metadata_id=new_metadata_service._id, include=("layers", "operations")
        )

        return new_md

    def update(self, service: Metadata, check_only: bool = 0) -> Metadata:
        """Update a metadata of service while keeping the associations of the layers.

        :param Metadata metadata: identifier of the resource to verify
        :param bool check_only: option to only get the diff

        :rtype: Metadata
        """
        # check metadata type
        if service.type != "service":
            raise TypeError(
                "This method applies only to metadata of web geo service. Use 'metadata.update instead'."
            )

        # check if layers and operations are present. If not, get it.
        if service.layers is None or service.operations is None:
            logger.debug(
                "Suresources 'layers' and 'operations' are required to properly update metadata of service. "
                "Let's retrieve these subresources..."
            )
            service = self.api_client.metadata.get(
                metadata_id=service._id, include=("layers", "operations")
            )

        # list all layers which have been associated
        li_associated_layers = [
            layer for layer in service.layers if layer.get("dataset") is not None
        ]

        # check only differences between layers
        if check_only:
            logger.error(
                NotImplementedError("It'll be implemented in a future version")
            )
            return service

        # or update the metadata
        if not len(li_associated_layers):
            logger.info(
                "Service has no layers associated with datasets. It could be updated without precaution."
            )
            service.layers = None
            # patch
            patch_srv = self.api_client.metadata.update(service)
        else:
            logger.info(
                "Service has {} layers associated with datasets. Updating metadata with precaution.".format(
                    len(li_associated_layers)
                )
            )
            # patch
            patch_srv = self.api_client.metadata.update(service)
            if isinstance(patch_srv, tuple):
                logger.error(
                    "Previous error 500 maybe occurred during PATCH because of a manual layer added to the service. "
                    "See: https://github.com/isogeo/isogeo-api/issues/5"
                )

        # check patching
        if isinstance(patch_srv, tuple):
            logger.error(
                "Previous error 500 maybe occurred during PATCH because of a manual layer added to the service. "
                "See: https://github.com/isogeo/isogeo-api/issues/5"
            )

        return self.api_client.metadata.get(
            metadata_id=service._id, include=("layers", "operations")
        )


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_metadata = ApiService()
