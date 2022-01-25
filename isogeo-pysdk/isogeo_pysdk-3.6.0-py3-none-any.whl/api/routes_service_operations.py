# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for ServiceOperations entities

    See: http://help.isogeo.com/api/complete/index.html#tag-operation
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import ServiceOperation, Metadata
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
class ApiServiceOperation:
    """Routes as methods of Isogeo API used to manipulate service_operations."""

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
        super(ApiServiceOperation, self).__init__()

    @ApiDecorators._check_bearer_validity
    def listing(self, metadata: Metadata) -> list:
        """Get all operations of a metadata service.

        :param Metadata metadata: metadata (resource) to edit. Must be type of service.
        """
        # check metadata type
        if metadata.type != "service":
            raise TypeError(
                "Operations routes are only available for metadata of services, not: {}".format(
                    metadata.type
                )
            )
        else:
            pass

        # URL
        url_service_operations = utils.get_request_base_url(
            route="resources/{}/operations/".format(metadata._id)
        )

        # request
        req_service_operations = self.api_client.get(
            url=url_service_operations,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_service_operations)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_service_operations.json()

    @ApiDecorators._check_bearer_validity
    def operation(self, metadata_id: str, operation_id: str) -> ServiceOperation:
        """Get details about a specific service operation and expand the model with the parent
        service metadata '_id' reference.

        :param str metadata_id: metadata with operations
        :param str operation_id: service operation UUID
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata_id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata_id)
            )
        else:
            pass

        # check service_operation UUID
        if not checker.check_is_uuid(operation_id):
            raise ValueError(
                "ServiceOperation ID is not a correct UUID: {}".format(operation_id)
            )
        else:
            pass

        # URL
        url_service_operation = utils.get_request_base_url(
            route="resources/{}/operations/{}".format(metadata_id, operation_id)
        )

        # request
        req_service_operation = self.api_client.get(
            url=url_service_operation,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_service_operation)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        service_operation_augmented = req_service_operation.json()
        service_operation_augmented["parent_resource"] = metadata_id

        # end of method
        return ServiceOperation(**service_operation_augmented)

    @ApiDecorators._check_bearer_validity
    def create(
        self, metadata: Metadata, operation: ServiceOperation
    ) -> ServiceOperation:
        """Add a new operation to a metadata (= resource).

        :param Metadata metadata: metadata (resource) to edit. Must be a service.
        :param ServiceOperation ServiceOperation: service_operation object to create
        """
        # check metadata type
        if metadata.type != "service":
            raise TypeError(
                "Operations routes are only available for metadata of services, not: {}".format(
                    metadata.type
                )
            )
        else:
            pass

        # URL
        url_service_operation_create = utils.get_request_base_url(
            route="resources/{}/operations/".format(metadata._id)
        )

        # request
        req_new_service_operation = self.api_client.post(
            url=url_service_operation_create,
            json=operation.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_service_operation)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        service_operation_augmented = req_new_service_operation.json()
        service_operation_augmented["parent_resource"] = metadata._id

        # end of method
        return ServiceOperation(**service_operation_augmented)

    # @ApiDecorators._check_bearer_validity
    # def delete(self, operation: ServiceOperation, metadata: Metadata = None):
    #     """Delete a service operation from Isogeo database.

    #     :param ServiceOperation operation: ServiceOperation model object to delete
    #     :param Metadata metadata: parent metadata (resource) containing the service_operation
    #     """
    #     # check service_operation UUID
    #     if not checker.check_is_uuid(operation._id):
    #         raise ValueError(
    #             "ServiceOperation ID is not a correct UUID: {}".format(operation._id)
    #         )
    #     else:
    #         pass

    #     # retrieve parent metadata
    #     if not checker.check_is_uuid(operation.parent_resource) and not metadata:
    #         raise ValueError(
    #             "ServiceOperation parent metadata is required. Requesting it..."
    #         )
    #     elif not checker.check_is_uuid(operation.parent_resource) and metadata:
    #         operation.parent_resource = metadata._id
    #     else:
    #         pass

    #     # URL
    #     url_service_operation_delete = utils.get_request_base_url(
    #         route="resources/{}/operations/{}".format(operation.parent_resource, operation._id)
    #     )

    #     # request
    #     req_service_operation_deletion = self.api_client.delete(
    #         url=url_service_operation_delete,
    #         headers=self.api_client.header,
    #         proxies=self.api_client.proxies,
    #         timeout=self.api_client.timeout,
    #         verify=self.api_client.ssl,
    #     )

    #     # checking response
    #     req_check = checker.check_api_response(req_service_operation_deletion)
    #     if isinstance(req_check, tuple):
    #         return req_check

    #     return req_service_operation_deletion

    # @ApiDecorators._check_bearer_validity
    # def update(self, operation: ServiceOperation, metadata: Metadata = None) -> ServiceOperation:
    #     """Update a service operation.

    #     :param ServiceOperation operation: ServiceOperation model object to update
    #     :param Metadata metadata: parent metadata (resource) containing the service_operation
    #     """
    #     # check service_operation UUID
    #     if not checker.check_is_uuid(operation._id):
    #         raise ValueError(
    #             "ServiceOperation ID is not a correct UUID: {}".format(operation._id)
    #         )
    #     else:
    #         pass

    #     # retrieve parent metadata
    #     if not checker.check_is_uuid(operation.parent_resource) and not metadata:
    #         raise ValueError(
    #             "ServiceOperation parent metadata is required. Requesting it..."
    #         )
    #     elif not checker.check_is_uuid(operation.parent_resource) and metadata:
    #         operation.parent_resource = metadata._id
    #     else:
    #         pass

    #     # URL
    #     url_service_operation_update = utils.get_request_base_url(
    #         route="resources/{}/operations/{}".format(operation.parent_resource, operation._id)
    #     )

    #     # request
    #     req_service_operation_update = self.api_client.put(
    #         url=url_service_operation_update,
    #         json=operation.to_dict_creation(),
    #         headers=self.api_client.header,
    #         proxies=self.api_client.proxies,
    #         verify=self.api_client.ssl,
    #         timeout=self.api_client.timeout,
    #     )

    #     # checking response
    #     req_check = checker.check_api_response(req_service_operation_update)
    #     if isinstance(req_check, tuple):
    #         return req_check

    #     # add parent resource id to keep tracking
    #     service_operation_augmented = req_service_operation_update.json()
    #     service_operation_augmented["parent_resource"] = operation.parent_resource

    #     # end of method
    #     return ServiceOperation(**service_operation_augmented)

    # # -- Routes to manage the related objects ------------------------------------------
    # @ApiDecorators._check_bearer_validity
    # def associate_metadata(
    #     self, service: Metadata, operation: ServiceOperation, dataset: Metadata
    # ) -> Response:
    #     """Associate a service operation with a dataset metadata.

    #     If the specified operation is already associated, the response is 409.

    #     :param Metadata service: metadata of the service which contains the operation
    #     :param ServiceOperation operation: operation model object to associate
    #     :param Metadata dataset: metadata of the dataset to associate with

    #     :Example:

    #     >>> # retrieve objects to be associated. First: the metadata of the service.
    #     >>> service = isogeo.metadata.get(
    #             metadata_id=str,
    #         )
    #     >>> # second: the operation of the service you want to associate
    #     >>> operation = isogeo.metadata.operations.operation(
    #             metadata_id=service._id,
    #             operation_id=str,
    #         )
    #     >>> # third: the dataset to be associated with the service operation
    #     >>> dataset = isogeo.metadata.get(
    #             metadata_id=str,
    #         )
    #     >>> # associate them
    #     >>> isogeo.metadata.operations.associate_metadata(
    #             service=service,
    #             operation=operation,
    #             dataset=metadata
    #         )
    #     """
    #     # check metadata UUID
    #     if not checker.check_is_uuid(service._id):
    #         raise ValueError(
    #             "Service metadata ID is not a correct UUID: {}".format(service._id)
    #         )
    #     else:
    #         pass

    #     # check operation UUID
    #     if not checker.check_is_uuid(operation._id):
    #         raise ValueError(
    #             "ServiceOperation ID is not a correct UUID: {}".format(operation._id)
    #         )
    #     else:
    #         pass

    #     # check dataset UUID
    #     if not checker.check_is_uuid(dataset._id):
    #         raise ValueError(
    #             "Dataset metadata ID is not a correct UUID: {}".format(dataset._id)
    #         )
    #     else:
    #         pass

    #     # check service metadata type
    #     if service.type != "service":
    #         raise TypeError(
    #             "Operations routes are only available for metadata of services, not: {}".format(
    #                 service.type
    #             )
    #         )
    #     else:
    #         pass

    #     # check dataset metadata type
    #     if dataset.type not in (
    #         "rasterDataset",
    #         "vectorDataset",
    #         "raster-dataset",
    #         "vector-dataset",
    #     ):
    #         raise TypeError(
    #             "Datasets association with operations routes are only available for metadata of datasets, not: {}".format(
    #                 dataset.type
    #             )
    #         )
    #     else:
    #         pass

    #     # URL
    #     url_operation_association = utils.get_request_base_url(
    #         route="resources/{}/operations/{}/dataset/{}".format(
    #             service._id, operation._id, dataset._id
    #         )
    #     )

    #     # request
    #     req_operation_association = self.api_client.post(
    #         url=url_operation_association,
    #         headers=self.api_client.header,
    #         proxies=self.api_client.proxies,
    #         verify=self.api_client.ssl,
    #         timeout=self.api_client.timeout,
    #     )

    #     # checking response
    #     req_check = checker.check_api_response(req_operation_association)
    #     if isinstance(req_check, tuple):
    #         # handle conflict (see: https://developer.mozilla.org/fr/docs/Web/HTTP/Status/409)
    #         if req_check[1] == 409:
    #             # log conflict
    #             logger.info(
    #                 "Operation is already associated with a dataset: '{}'. Isogeo API doesn't allow to create duplicates (HTTP {} - {}).".format(
    #                     operation.name, req_check[1], req_operation_association.reason
    #                 )
    #             )
    #         else:
    #             # if other error, then return it
    #             return req_check

    #     # end of method
    #     return req_operation_association

    # @ApiDecorators._check_bearer_validity
    # def dissociate_metadata(
    #     self, service: Metadata, operation: ServiceOperation, dataset: Metadata
    # ) -> Response:
    #     """Removes the association between a a service operation with a dataset metadata.

    #     If the association doesn't exist, the response is 404.

    #     :param Metadata service: metadata of the service which contains the operation
    #     :param ServiceOperation operation: operation model object to associate
    #     :param Metadata dataset: metadata of the dataset to associate with
    #     """
    #     # check metadata UUID
    #     if not checker.check_is_uuid(service._id):
    #         raise ValueError(
    #             "Service metadata ID is not a correct UUID: {}".format(service._id)
    #         )
    #     else:
    #         pass

    #     # check operation UUID
    #     if not checker.check_is_uuid(operation._id):
    #         raise ValueError(
    #             "ServiceOperation ID is not a correct UUID: {}".format(operation._id)
    #         )
    #     else:
    #         pass

    #     # check dataset UUID
    #     if not checker.check_is_uuid(dataset._id):
    #         raise ValueError(
    #             "Dataset metadata ID is not a correct UUID: {}".format(dataset._id)
    #         )
    #     else:
    #         pass

    #     # check service metadata type
    #     if service.type != "service":
    #         raise TypeError(
    #             "Operations routes are only available for metadata of services, not: {}".format(
    #                 service.type
    #             )
    #         )
    #     else:
    #         pass

    #     # check dataset metadata type
    #     if dataset.type not in (
    #         "rasterDataset",
    #         "vectorDataset",
    #         "raster-dataset",
    #         "vector-dataset",
    #     ):
    #         raise TypeError(
    #             "Datasets association with operations routes are only available for metadata of datasets, not: {}".format(
    #                 dataset.type
    #             )
    #         )
    #     else:
    #         pass

    #     # URL
    #     url_operation_dissociation = utils.get_request_base_url(
    #         route="resources/{}/operations/{}/dataset/{}".format(
    #             service._id, operation._id, dataset._id
    #         )
    #     )

    #     # request
    #     req_operation_dissociation = self.api_client.delete(
    #         url=url_operation_dissociation,
    #         headers=self.api_client.header,
    #         proxies=self.api_client.proxies,
    #         verify=self.api_client.ssl,
    #         timeout=self.api_client.timeout,
    #     )

    #     # checking response
    #     req_check = checker.check_api_response(req_operation_dissociation)
    #     if isinstance(req_check, tuple):
    #         return req_check

    #     # end of method
    #     return req_operation_dissociation


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_service_operation = ApiServiceOperation()
