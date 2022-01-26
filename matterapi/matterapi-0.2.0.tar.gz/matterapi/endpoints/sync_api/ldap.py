from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ...models import (
    LDAPGroupsPaged,
    MigrateAuthToLdapJsonBody,
    MigrateIdLdapJsonBody,
    StatusOK,
    UploadLdapPrivateCertificateMultipartData,
    UploadLdapPublicCertificateMultipartData,
)
from ..base import ApiBaseClass


class LdapApi(ApiBaseClass):
    """Endpoints for configuring and interacting with LDAP."""

    def migrate_auth_to_ldap(
        self,
        *,
        json_body: MigrateAuthToLdapJsonBody,
    ) -> None:
        """Migrate user accounts authentication type to LDAP.

        Migrates accounts from one authentication provider to another. For
        example, you can upgrade your authentication provider from email to
        LDAP.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.28
        """

        url = "/users/migrate_auth/ldap".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response

    def sync_ldap(
        self,
    ) -> StatusOK:
        """Sync with LDAP

        Synchronize any user attribute changes in the configured AD/LDAP server
        with Mattermost.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/ldap/sync".format()

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def test_ldap(
        self,
    ) -> StatusOK:
        """Test LDAP configuration

        Test the current AD/LDAP configuration to see if the AD/LDAP server can
        be contacted successfully.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/ldap/test".format()

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def get_ldap_groups(
        self,
        *,
        q: Optional[str] = None,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[LDAPGroupsPaged]:
        """Returns a list of LDAP groups



        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/ldap/groups".format()
        params: Dict[str, Any] = {
            "q": q,
            "page": page,
            "per_page": per_page,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = LDAPGroupsPaged.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def link_ldap_group(
        self,
        remote_id: str,
    ) -> StatusOK:
        """Link a LDAP group



        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/ldap/groups/{remote_id}/link".format(
            remote_id=remote_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = StatusOK.parse_obj(response.json())

            return response_201
        return response

    def migrate_id_ldap(
        self,
        *,
        json_body: MigrateIdLdapJsonBody,
    ) -> StatusOK:
        """Migrate Id LDAP

        Migrate LDAP IdAttribute to new value.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.26
        """

        url = "/ldap/migrateid".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def upload_ldap_public_certificate(
        self,
        *,
        multipart_data: UploadLdapPublicCertificateMultipartData,
    ) -> StatusOK:
        """Upload public certificate

        Upload the public certificate to be used for TLS verification. The
        server will pick a hard-coded filename for the PublicCertificateFile
        setting in your `config.json`.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/ldap/certificate/public".format()

        multipart_body_data = UploadLdapPublicCertificateMultipartData.parse_obj(
            multipart_data
        )

        request_kwargs = {
            "url": url,
            "data": multipart_body_data.get_data(),
            "files": multipart_body_data.get_files(),
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def delete_ldap_public_certificate(
        self,
    ) -> StatusOK:
        """Remove public certificate

        Delete the current public certificate being used for TLS verification.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/ldap/certificate/public".format()

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def upload_ldap_private_certificate(
        self,
        *,
        multipart_data: UploadLdapPrivateCertificateMultipartData,
    ) -> StatusOK:
        """Upload private key

        Upload the private key to be used for TLS verification. The server will
        pick a hard-coded filename for the PrivateKeyFile setting in your
        `config.json`.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/ldap/certificate/private".format()

        multipart_body_data = UploadLdapPrivateCertificateMultipartData.parse_obj(
            multipart_data
        )

        request_kwargs = {
            "url": url,
            "data": multipart_body_data.get_data(),
            "files": multipart_body_data.get_files(),
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def delete_ldap_private_certificate(
        self,
    ) -> StatusOK:
        """Remove private key

        Delete the current private key being used with your TLS verification.

        Permissions:
            Must have `manage_system` permission.
        """

        url = "/ldap/certificate/private".format()

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response
