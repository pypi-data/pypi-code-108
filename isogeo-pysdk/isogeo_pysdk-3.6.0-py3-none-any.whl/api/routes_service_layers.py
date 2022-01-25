# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for ServiceLayers entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# 3rd party
from requests.models import Response

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import ServiceLayer, Metadata
from isogeo_pysdk.utils import IsogeoUtils

# #############################################################################
# ########## Global ################
# ##################################

logger = logging.getLogger(__name__)
checker = IsogeoChecker()
utils = IsogeoUtils()


# #############################################################################
# ########## Classes ###############
# ##################################
class ApiServiceLayer:
    """Routes as methods of Isogeo API used to manipulate service_layers."""

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
        super(ApiServiceLayer, self).__init__()

    @ApiDecorators._check_bearer_validity
    def listing(self, metadata: Metadata) -> list:
        """Get all service layers of a metadata.

        :param Metadata metadata: metadata (resource) to edit
        """
        # check metadata type
        if metadata.type != "service":
            raise TypeError(
                "Layers routes are only available for metadata of services, not: {}".format(
                    metadata.type
                )
            )
        else:
            pass

        # URL
        url_service_layers = utils.get_request_base_url(
            route="resources/{}/layers/".format(metadata._id)
        )

        # request
        req_service_layers = self.api_client.get(
            url=url_service_layers,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_service_layers)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_service_layers.json()

    @ApiDecorators._check_bearer_validity
    def layer(self, metadata_id: str, layer_id: str) -> ServiceLayer:
        """Get details about a specific service_layer.

        :param str metadata_id: metadata with layers
        :param str layer_id: service layer UUID
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata_id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata_id)
            )
        else:
            pass

        # check service_layer UUID
        if not checker.check_is_uuid(layer_id):
            raise ValueError(
                "ServiceLayer ID is not a correct UUID: {}".format(layer_id)
            )
        else:
            pass

        # URL
        url_service_layer = utils.get_request_base_url(
            route="resources/{}/layers/{}".format(metadata_id, layer_id)
        )

        # request
        req_service_layer = self.api_client.get(
            url=url_service_layer,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_service_layer)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        service_layer_augmented = req_service_layer.json()
        service_layer_augmented["parent_resource"] = metadata_id

        # end of method
        return ServiceLayer(**service_layer_augmented)

    @ApiDecorators._check_bearer_validity
    def create(self, metadata: Metadata, layer: ServiceLayer) -> ServiceLayer:
        """Add a new layer to a metadata (= resource).

        :param Metadata metadata: metadata (resource) to edit. Must be a service.
        :param ServiceLayer ServiceLayer: service_layer object to create
        """
        # check metadata type
        if metadata.type != "service":
            raise TypeError(
                "Layers routes are only available for metadata of services, not: {}".format(
                    metadata.type
                )
            )
        else:
            pass

        # URL
        url_service_layer_create = utils.get_request_base_url(
            route="resources/{}/layers/".format(metadata._id)
        )

        # request
        req_new_service_layer = self.api_client.post(
            url=url_service_layer_create,
            json=layer.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_service_layer)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        service_layer_augmented = req_new_service_layer.json()
        service_layer_augmented["parent_resource"] = metadata._id

        # end of method
        return ServiceLayer(**service_layer_augmented)

    @ApiDecorators._check_bearer_validity
    def delete(self, layer: ServiceLayer, metadata: Metadata = None):
        """Delete a service layer from Isogeo database.

        :param ServiceLayer layer: ServiceLayer model object to delete
        :param Metadata metadata: parent metadata (resource) containing the service_layer
        """
        # check service_layer UUID
        if not checker.check_is_uuid(layer._id):
            raise ValueError(
                "ServiceLayer ID is not a correct UUID: {}".format(layer._id)
            )
        else:
            pass

        # retrieve parent metadata
        if not checker.check_is_uuid(layer.parent_resource) and not metadata:
            raise ValueError(
                "ServiceLayer parent metadata is required. Requesting it..."
            )
        elif not checker.check_is_uuid(layer.parent_resource) and metadata:
            layer.parent_resource = metadata._id
        else:
            pass

        # URL
        url_service_layer_delete = utils.get_request_base_url(
            route="resources/{}/layers/{}".format(layer.parent_resource, layer._id)
        )

        # request
        req_service_layer_deletion = self.api_client.delete(
            url=url_service_layer_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_service_layer_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_service_layer_deletion

    @ApiDecorators._check_bearer_validity
    def update(self, layer: ServiceLayer, metadata: Metadata = None) -> ServiceLayer:
        """Update a service layer.

        :param ServiceLayer layer: ServiceLayer model object to update
        :param Metadata metadata: parent metadata (resource) containing the service_layer
        """
        # check service_layer UUID
        if not checker.check_is_uuid(layer._id):
            raise ValueError(
                "ServiceLayer ID is not a correct UUID: {}".format(layer._id)
            )
        else:
            pass

        # retrieve parent metadata
        if not checker.check_is_uuid(layer.parent_resource) and not metadata:
            raise ValueError(
                "ServiceLayer parent metadata is required. Requesting it..."
            )
        elif not checker.check_is_uuid(layer.parent_resource) and metadata:
            layer.parent_resource = metadata._id
        else:
            pass

        # URL
        url_service_layer_update = utils.get_request_base_url(
            route="resources/{}/layers/{}".format(layer.parent_resource, layer._id)
        )

        # request
        req_service_layer_update = self.api_client.put(
            url=url_service_layer_update,
            json=layer.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_service_layer_update)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        service_layer_augmented = req_service_layer_update.json()
        service_layer_augmented["parent_resource"] = layer.parent_resource

        # end of method
        return ServiceLayer(**service_layer_augmented)

    # -- Routes to manage the related objects ------------------------------------------
    @ApiDecorators._check_bearer_validity
    def associate_metadata(
        self, service: Metadata, layer: ServiceLayer, dataset: Metadata
    ) -> Response:
        """Associate a service layer with a dataset metadata.

        If the specified layer is already associated, the response is 409.

        :param Metadata service: metadata of the service which contains the layer
        :param ServiceLayer layer: layer model object to associate
        :param Metadata dataset: metadata of the dataset to associate with

        :Example:

        >>> # retrieve objects to be associated. First: the metadata of the service.
        >>> service = isogeo.metadata.get(
                metadata_id=str,
            )
        >>> # second: the layer of the service you want to associate
        >>> layer = isogeo.metadata.layers.layer(
                metadata_id=service._id,
                layer_id=str,
            )
        >>> # third: the dataset to be associated with the service layer
        >>> dataset = isogeo.metadata.get(
                metadata_id=str,
            )
        >>> # associate them
        >>> isogeo.metadata.layers.associate_metadata(
                service=service,
                layer=layer,
                dataset=metadata
            )
        """
        # check metadata UUID
        if not checker.check_is_uuid(service._id):
            raise ValueError(
                "Service metadata ID is not a correct UUID: {}".format(service._id)
            )
        else:
            pass

        # check layer UUID
        if not checker.check_is_uuid(layer._id):
            raise ValueError(
                "ServiceLayer ID is not a correct UUID: {}".format(layer._id)
            )
        else:
            pass

        # check dataset UUID
        if not checker.check_is_uuid(dataset._id):
            raise ValueError(
                "Dataset metadata ID is not a correct UUID: {}".format(dataset._id)
            )
        else:
            pass

        # check service metadata type
        if service.type != "service":
            raise TypeError(
                "Layers routes are only available for metadata of services, not: {}".format(
                    service.type
                )
            )
        else:
            pass

        # check dataset metadata type
        if dataset.type not in (
            "rasterDataset",
            "vectorDataset",
            "raster-dataset",
            "vector-dataset",
        ):
            raise TypeError(
                "Datasets association with layers routes are only available for metadata of datasets, not: {}".format(
                    dataset.type
                )
            )
        else:
            pass

        # URL
        url_layer_association = utils.get_request_base_url(
            route="resources/{}/layers/{}/dataset/{}".format(
                service._id, layer._id, dataset._id
            )
        )

        # request
        req_layer_association = self.api_client.post(
            url=url_layer_association,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_layer_association)
        if isinstance(req_check, tuple):
            # handle conflict (see: https://developer.mozilla.org/fr/docs/Web/HTTP/Status/409)
            if req_check[1] == 409:
                # log conflict
                logger.info(
                    "Layer is already associated with a dataset: '{}'. Isogeo API doesn't allow to create duplicates (HTTP {} - {}).".format(
                        layer.name, req_check[1], req_layer_association.reason
                    )
                )
            else:
                # if other error, then return it
                return req_check

        # end of method
        return req_layer_association

    @ApiDecorators._check_bearer_validity
    def dissociate_metadata(
        self, service: Metadata, layer: ServiceLayer, dataset: Metadata
    ) -> Response:
        """Removes the association between a a service layer with a dataset metadata.

        If the association doesn't exist, the response is 404.

        :param Metadata service: metadata of the service which contains the layer
        :param ServiceLayer layer: layer model object to associate
        :param Metadata dataset: metadata of the dataset to associate with
        """
        # check metadata UUID
        if not checker.check_is_uuid(service._id):
            raise ValueError(
                "Service metadata ID is not a correct UUID: {}".format(service._id)
            )
        else:
            pass

        # check layer UUID
        if not checker.check_is_uuid(layer._id):
            raise ValueError(
                "ServiceLayer ID is not a correct UUID: {}".format(layer._id)
            )
        else:
            pass

        # check dataset UUID
        if not checker.check_is_uuid(dataset._id):
            raise ValueError(
                "Dataset metadata ID is not a correct UUID: {}".format(dataset._id)
            )
        else:
            pass

        # check service metadata type
        if service.type != "service":
            raise TypeError(
                "Layers routes are only available for metadata of services, not: {}".format(
                    service.type
                )
            )
        else:
            pass

        # check dataset metadata type
        if dataset.type not in (
            "rasterDataset",
            "vectorDataset",
            "raster-dataset",
            "vector-dataset",
        ):
            raise TypeError(
                "Datasets association with layers routes are only available for metadata of datasets, not: {}".format(
                    dataset.type
                )
            )
        else:
            pass

        # URL
        url_layer_dissociation = utils.get_request_base_url(
            route="resources/{}/layers/{}/dataset/{}".format(
                service._id, layer._id, dataset._id
            )
        )

        # request
        req_layer_dissociation = self.api_client.delete(
            url=url_layer_dissociation,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_layer_dissociation)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_layer_dissociation


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_service_layer = ApiServiceLayer()
