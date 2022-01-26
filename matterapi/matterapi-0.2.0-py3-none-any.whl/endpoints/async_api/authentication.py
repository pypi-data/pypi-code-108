from pydantic import BaseModel

from ...models import MigrateAuthToLdapJsonBody, MigrateAuthToSamlJsonBody
from ..base import ApiBaseClass


class AuthenticationApi(ApiBaseClass):
    """Endpoint related to authentication operations"""

    async def migrate_auth_to_ldap(
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response

    async def migrate_auth_to_saml(
        self,
        *,
        json_body: MigrateAuthToSamlJsonBody,
    ) -> None:
        """Migrate user accounts authentication type to SAML.

        Migrates accounts from one authentication provider to another. For
        example, you can upgrade your authentication provider from email to
        SAML.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.28
        """

        url = "/users/migrate_auth/saml".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response
