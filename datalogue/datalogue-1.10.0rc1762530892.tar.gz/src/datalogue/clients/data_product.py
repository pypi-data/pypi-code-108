from uuid import UUID
from typing import List

from datalogue.models.permission import Permission, SharePermission, UnsharePermission, ObjectType, Scope
from datalogue.dtl_utils import is_valid_uuid
from datalogue.clients._http import _HttpClient, Union, HttpMethod, Optional
from datalogue.dtl_utils import _parse_list
from datalogue.errors import DtlError
from datalogue.models.data_product import DataProduct


class DataProductClient:
    """
    Client to interact with the Data Products
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def create(self, data_product: DataProduct) -> Union[DtlError, DataProduct]:
        """
        Creates a Data Product

        :param data_product: A Data Product object that user wants to create

        Restrictions:
        * data product naming must be unique

        :return: Returns created Data Product object if successful, or DtlError if failed
        """
        payload = data_product._as_payload()
        res = self.http_client.make_authed_request(self.service_uri + "/data-products", HttpMethod.POST, payload)

        if isinstance(res, DtlError):
            return res

        return DataProduct._from_payload(res)

    def update(
        self, id: UUID, name: Optional[str] = None, description: Optional[str] = None
    ) -> Union[DtlError, DataProduct]:
        """
        Updates a Data Product

        :param id: id of the Data Product to be updated
        :param name: New name to be applied to the data product (if 'name' is not being updated, `description` should be updated)
        :param description: New description to be applied to the data product (if 'description' is not being updated, `name` should be updated)
        :return: Returns an updated Data Product object if successful, or DtlError if failed
        """
        payload = {}

        if is_valid_uuid(id) is False:
            return DtlError("id provided is not a valid UUID format.")

        if name is None and description is None:
            return DtlError("Either name or description must be mentioned to update a Data Product")

        if name is not None:
            payload["name"] = name

        if description is not None:
            payload["description"] = description

        res = self.http_client.make_authed_request(self.service_uri + f"/data-products/{id}", HttpMethod.PUT, payload)

        if isinstance(res, DtlError):
            return res

        return DataProduct._from_payload(res)

    def get(self, id: UUID) -> Union[DtlError, DataProduct]:
        """
        Retrieve a Data Product by its id.

        :param id: id of an existing Data Product to be retrieved
        :return: Data Product object if successful, or DtlError if failed
        """
        if is_valid_uuid(id) is False:
            return DtlError("id provided is not a valid UUID format.")
        res = self.http_client.make_authed_request(self.service_uri + f"/data-products/{id}", HttpMethod.GET)
        if isinstance(res, DtlError):
            return res
        return DataProduct._from_payload(res)

    def add_pipelines(self, data_product_id: UUID, pipeline_ids: List[UUID]) -> Union[DtlError, DataProduct]:
        """
        Add Pipelines to a Data Product.

        :param data_product_id: id of the Data Product
        :param pipeline_ids: ids of the pipelines that need to be added to a Data Product

        :Restrictions:
        * a pipeline can belong only to one data product at a time

        :return: updated Data Product object if successful, or DtlError if failed
        """
        if is_valid_uuid(data_product_id) is False:
            return DtlError("data_product_id provided is not a valid UUID format.")
        if len(pipeline_ids) == 0:
            return DtlError("Please specify at least 1 pipeline id under pipeline_ids")
        else:
            payload = {"streamIds": [str(pipeline_id) for pipeline_id in pipeline_ids], "streamAction": "add"}

        res = self.http_client.make_authed_request(
            self.service_uri + f"/data-products/{data_product_id}/streams", HttpMethod.POST, payload
        )
        if isinstance(res, DtlError):
            return res
        return DataProduct._from_payload(res)

    def remove_pipelines(self, data_product_id: UUID, pipeline_ids: List[UUID]) -> Union[DtlError, DataProduct]:
        """
        Remove Pipelines from a Data Product.

        :param data_product_id: id of the Data Product
        :param pipeline_ids: ids of the pipelines to be removed from a Data Product
        :return: updated Data Product object if successful, or DtlError if failed
        """
        if is_valid_uuid(data_product_id) is False:
            return DtlError("data_product_id provided is not a valid UUID format.")
        if len(pipeline_ids) == 0:
            return DtlError("Please specify at least 1 pipeline id under pipeline_ids")
        else:
            payload = {"streamIds": [str(pipeline_id) for pipeline_id in pipeline_ids], "streamAction": "remove"}

        res = self.http_client.make_authed_request(
            self.service_uri + f"/data-products/{data_product_id}/streams", HttpMethod.POST, payload
        )
        if isinstance(res, DtlError):
            return res
        return DataProduct._from_payload(res)

    def delete(self, data_product_id: UUID, delete_pipelines: bool = True) -> Union[DtlError, bool]:
        """
        Deletes the given Data Product

        :param data_product_id: id of the data product to be deleted
        :param delete_pipelines: cascade delete all pipelines with permissions of this Data Product, default True
        :return: true if successful, DtlError otherwise
        """
        if is_valid_uuid(data_product_id) is False:
            return DtlError("id provided is not a valid UUID format.")
        res = self.http_client.make_authed_request(
            self.service_uri + f"/data-products/{data_product_id}?delete-streams={delete_pipelines}", HttpMethod.DELETE
        )
        if isinstance(res, DtlError):
            return res
        else:
            return True

    def list(self, by_name: str = "", page: int = 1, size: int = 25) -> Union[DtlError, List[DataProduct]]:
        """
        List all the data products that are saved

        :param by_name: optionally filter your list by data product names, containing the supplied keyword, default ''
        :param page: page to be retrieved, default 1
        :param size: number of items to be put in a page, default 25
        :return: Returns a List of all the available data products or DtlError
        """
        params = {"page": page, "size": size, "search-in-name": by_name}
        res = self.http_client.make_authed_request(
            path=self.service_uri + f"/data-products", method=HttpMethod.GET, params=params
        )
        if isinstance(res, DtlError):
            return res
        return _parse_list(DataProduct._from_payload)(res)

    def share(
        self,
        data_product_id: UUID,
        target_type: Scope,
        target_id: UUID,
        permission: Permission,
        share_all_pipelines: bool = True,
    ) -> Union[SharePermission, DtlError]:
        """
        Share the Data Product, and optionally its pipelines.

        :param data_product_id: id of the Data Product that is to be shared
        :param target_type: Scope (`User`, `Group`) with whom you want to share the template. It can be User, or Group.
        :param target_id: id of the User/Group you want to share with
        :param permission: Permission (`Read`/`Write`/`Share`) to be shared for the Data Product.
        :param share_all_pipelines: cascade permission sharing to all pipelines of this Data Product,
        that are accessible by the requesting user, default True
        :return: Returns a SharePermission for the specific Data Product if successful, or DtlError if failed
        """
        if isinstance(target_type, str) and target_type not in Scope._value2member_map_:
            return DtlError(f"target_type: {target_type} is invalid. It can be `User` or `Group`")
        if isinstance(permission, str) and permission not in Permission._value2member_map_:
            return DtlError(f"permission: {permission} is invalid. It can be `Read`, `Write` or `Share`")
        params = {
            "targetType": target_type.value,
            "targetId": f"{target_id}",
            "permission": permission.value,
            "update-all-stream-permissions": share_all_pipelines,
        }
        rsp = self.http_client.make_authed_request(
            path=f"{self.service_uri}/data-products/{str(data_product_id)}/shares",
            method=HttpMethod.POST,
            params=params,
        )

        if isinstance(rsp, DtlError):
            return rsp

        return SharePermission(ObjectType.DataProduct, target_id, target_type, permission)

    def unshare(
        self,
        data_product_id: UUID,
        target_type: Scope,
        target_id: UUID,
        permission: Permission,
        unshare_all_pipelines: bool = True,
        exclude_pipeline_ids: Optional[List[UUID]] = None,
    ) -> Union[DtlError, UnsharePermission]:
        """
        Unshare the Data Product, and/or all of its accessible pipelines
        (excluding pipeline_ids supplied by the requesting user).

        :param data_product_id: id of the Data Product that is to be unshared
        :param target_type: Scope (`User`, `Group`) you want to unshare the Data Product with. It can be User, or Group.
        :param target_id: id of the User/Group you want to unshare with
        :param permission: existing permission (`Read`/`Write`/`Share`) of the Data Product, that you want to revoke
        :param unshare_all_pipelines: cascade permission unsharing to all pipelines of Data Product, that
        are accessible by the requesting user (except exclude_pipeline_ids), default True
        :param exclude_pipeline_ids: A list of pipeline_ids, that will not be unshared, while unsharing Data Product
        :return: Returns a UnsharePermission for the specific Data Product if successful, or DtlError if failed
        """

        if isinstance(target_type, str) and target_type not in Scope._value2member_map_:
            return DtlError(f"target_type: {target_type} is invalid. It can be `User` or `Group`")
        if isinstance(permission, str) and permission not in Permission._value2member_map_:
            return DtlError(f"permission: {permission} is invalid. It can be `Read`, `Write` or `Share`")
        params = {
            "targetType": target_type.value,
            "targetId": f"{target_id}",
            "permission": permission.value,
            "update-all-stream-permissions": unshare_all_pipelines,
        }
        if exclude_pipeline_ids is not None:
            params["exclude-stream-ids"] = exclude_pipeline_ids

        rsp = self.http_client.make_authed_request(
            path=f"{self.service_uri}/data-products/{str(data_product_id)}/shares",
            method=HttpMethod.DELETE,
            params=params,
        )

        if isinstance(rsp, DtlError):
            return rsp

        return UnsharePermission(ObjectType.DataProduct, target_id, target_type, permission)
