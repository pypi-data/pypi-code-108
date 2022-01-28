from typing import List, Union, Optional

from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.models.datastore import Datastore, CredentialType
from datalogue.models.credentials import (
    Credentials,
    _credentials_ref_from_payload,
    CredentialsReference,
)
from datalogue.dtl_utils import _parse_list
from uuid import UUID
from datalogue.errors import DtlError
from datalogue.models.permission import CredentialPermission


class CredentialsClient:
    """
    Client to interact with the Credentials objects
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def list(
        self, credential_type: Optional[str] = None, page: int = 1, item_per_page: int = 25,
    ) -> Union[DtlError, List[Datastore]]:
        """
        Lists available credentials that user has Use Permission

        :param credential_type: type of the credentials (S3, GCS, Jdbc, etc)
        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available credentials or an error message as a string
        """

        res = self.http_client.make_authed_request(
            self.service_uri
            + f"/credentials?page={page}&size={item_per_page}{'' if credential_type is None else f'&type={credential_type}'}",
            HttpMethod.GET,
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(_credentials_ref_from_payload)(res)

    def create(
        self,
        credentials_definition: Credentials,
        name: Optional[str] = None,
        is_destination: Optional[bool] = False,
        data_models: [UUID] = [],
        load_schema_and_samples: Optional[bool] = False,
    ) -> Union[DtlError, CredentialsReference]:
        """
        Creates the Credentials as specified.

        :param credentials_definition: Credentials Definition to be creates
        :param name: Name to be given to the Credentials to be able to find it later
        :param is_destination: Boolean to specify if credential refers to a destination or not.
        :param data_models: List of data model UUIDs that are related to the data in the specified credentials.
        :param load_schema_and_samples: If True, the sampling and schema extraction will be performed automatically for
         all datastores of this credential (False by default) (temporarily disabled)
        :return: string with error message if failed, uuid otherwise
        """
        load_schema_and_samples = False

        payload = credentials_definition._as_payload()

        if credentials_definition.type == CredentialType.S3:
            if load_schema_and_samples is True and "connectionBucket" not in payload:
                return DtlError("`connection_bucket` must be supplied, when `load_schema_and_samples` is True")

        res = self.http_client.make_authed_request(
            self.service_uri + "/credentials",
            HttpMethod.POST,
            {
                "name": name,
                "credentials": payload,
                "isDestination": is_destination,
                "dataModels": data_models,
                "loadSchemaAndSamples": load_schema_and_samples,
            },
        )

        if isinstance(res, DtlError):
            return res

        return _credentials_ref_from_payload(res)

    def update(
        self, credentials_id: UUID, credentials_definition: Credentials, name: Optional[str] = None,
    ) -> Union[DtlError, CredentialsReference]:
        """
        Updates the given Credentials id with name and credentials

        TODO rework the api so that you can only update the name without the Credentials themselves

        :param credentials_id: id of te Credentials to update
        :param name: if specified, will overwrite current name
        :param credentials_definition: new Credentials definition
        :return:
        """

        body = {}
        if name is not None:
            body["name"] = name

        body["credentials"] = credentials_definition._as_payload()

        res = self.http_client.make_authed_request(
            self.service_uri + "/credentials/" + str(credentials_id), HttpMethod.PUT, body,
        )

        if isinstance(res, DtlError):
            return res

        return _credentials_ref_from_payload(res)

    def delete(self, credentials_id: UUID) -> Union[DtlError, bool]:
        """
        Deletes the given Credentials

        :param credentials_id: id of the credentials to be deleted
        :return: true if successful, false otherwise
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/credentials/" + str(credentials_id), HttpMethod.DELETE
        )

        if isinstance(res, DtlError):
            return res
        else:
            return True

    def share(self, credentials_id: UUID, group_id: UUID, permission: CredentialPermission) -> Union[DtlError, bool]:
        """
        Shares the given Credentials

        :param credentials_id: id of the credentials to be shared
        :param group_id: id of the group to be shared with
        :param permission: level of the Permission
        :return: true if successful, false otherwise
        """
        res = self.http_client.make_authed_request(
            self.service_uri
            + f"/credentials/{str(credentials_id)}/permissions/groups/{str(group_id)}/{str(permission.value)}",
            HttpMethod.PUT,
        )

        if isinstance(res, DtlError):
            return res

        return True

    def validate(
        self, credentials_id: Optional[Union[str, UUID]] = None, credentials_definition: Optional[Credentials] = None,
    ) -> Union[bool, DtlError]:
        """
        Validate that credentials can access data; usable with created credentials or a local Credentials object

        :param credentials_id: id of the credentials you wish to validate
        :param credentials_definition: local definition of a Credentials object; for pre-creation validation
        :return: True if successful, or DtlError if failed
        """

        if credentials_id is not None and credentials_definition is not None:
            return DtlError(
                "Both credentials_id & credentials_definition cannot be specified together for validating credentials"
            )

        if credentials_id is not None:
            res = self.http_client.make_authed_request(
                self.service_uri + f"/credentials/{str(credentials_id)}/test", HttpMethod.POST,
            )
        elif credentials_definition is not None:
            res = self.http_client.make_authed_request(
                self.service_uri + "/credentials/test",
                HttpMethod.POST,
                {"credentials": credentials_definition._as_payload(), "name": ""},
            )

        else:
            res = DtlError("Either credentials_id or credentials_definition must be supplied to validate credentials")

        if isinstance(res, DtlError):
            return res

        return True
