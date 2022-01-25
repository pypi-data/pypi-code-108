import json
from typing import Dict, Optional

import click
from gql import gql


class CredentialsMixin:
    """
    Mixin adding properties to the Grid client. This mixin adds
    all credential methods.
    """
    def __init__(self):
        pass

    def get_credentials(self):
        query = gql(
            """
        query {
            getUserCredentials {
                credentialId
                provider
                alias
                createdAt
                lastUsedAt
                defaultCredential
            }
        }
        """
        )
        result = self.client.execute(query)
        return result

    def credentials_add(self, provider: str, credentials: Dict[str, str], alias: str, description: str) -> None:
        """Adds a new credential set to Grid."""
        mutation = gql(
            """
            mutation (
                $provider: String!
                $credentials: JSONString!
                $alias: String
                $description: String
                ) {
                createCloudCredential (
                    properties: {
                                provider: $provider
                                credentials: $credentials
                                alias: $alias
                                description: $description
                            }
                ) {
                success
                message
                }
            }
            """
        )
        params = {
            'provider': provider,
            'credentials': json.dumps(credentials),
            'alias': alias,
            'description': description
        }
        result = self.client.execute(mutation, variable_values=params)
        click.echo(result['createCloudCredential']['message'])

    def credentials_update(
        self,
        credential_id: str,
        alias: Optional[str] = None,
        description: Optional[str] = None,
        is_default: Optional[bool] = None
    ):
        """Updates a credential set in the Grid backend."""
        mutation = gql(
            """
            mutation UpdateCredential (
                $credentialId: ID!
                $alias: String
                $description: String
                $isDefault: Boolean
            ) {
                updateCloudCredential (
                    credentialId: $credentialId
                    alias: $alias
                    description: $description
                    isDefault: $isDefault
                ) {
                    success
                    message
                }
            }
            """
        )

        params = {'credentialId': credential_id, 'alias': alias, 'description': description, 'isDefault': is_default}

        result = self.client.execute(mutation, variable_values=params)
        click.echo(result['updateCloudCredential']['message'])
        click.echo(f"Set default credentials to ID {credential_id}.")

    def credentials_delete(self):  # pragma: no cover
        pass
