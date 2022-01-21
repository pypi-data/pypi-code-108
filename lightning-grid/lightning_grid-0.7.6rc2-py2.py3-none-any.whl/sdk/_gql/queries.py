from typing import List, Optional

from grid.metadata import __version__
from grid.sdk.client import create_gql_client
from grid.sdk.client.grid_gql import gql_execute


def get_grid_user_id(client) -> str:
    query = """
    query Login ($cliVersion: String!) {
        cliLogin (cliVersion: $cliVersion) {
            userId
            success
            message
        }
    }
    """
    res = gql_execute(client, query, cliVersion=__version__)['cliLogin']
    return res['userId']


def get_user_basic_info():
    client = create_gql_client()
    query = """
    query {
        getUser {
            userId
            isVerified
            completedSignup
            isBlocked
            username
            firstName
            lastName
            email
        }
    }
    """
    return gql_execute(client, query)['getUser']


def get_user_teams() -> List[dict]:
    client = create_gql_client()
    query = """
        query GetUserTeams {
            getUserTeams {
                success
                message
                teams {
                    id
                    name
                    createdAt
                    role
                    members {
                        id
                        username
                        firstName
                        lastName
                    }
                }
            }
        }
    """
    result = gql_execute(client, query)
    if not result['getUserTeams'] or not result['getUserTeams']['success']:
        raise RuntimeError(result['getUserTeams']["message"])
    return result['getUserTeams']['teams']


def get_user_info():
    """Return basic information about a user."""
    client = create_gql_client()
    query = """
        query {
            getUser {
                username
                firstName
                lastName
                email

            }
        }
    """

    result = gql_execute(client, query)
    if not result['getUser']:
        raise RuntimeError(result['getUser']["message"])
    return result['getUser']


def get_available_datastores(team_id: Optional[str] = None):
    client = create_gql_client()
    query = """
        query GetDatastores ($teamId: ID){
            getDatastores(teamId: $teamId) {
                id
                name
                version
                size
                createdAt
                snapshotStatus
                clusterId
                userDetails {
                    id
                    username
                    firstName
                    lastName
                }
            }
        }
    """
    params = {'teamId': team_id}
    result = gql_execute(client, query, **params)
    return result['getDatastores']


def delete_datastore(name: str, version: int, cluster: Optional[str] = None):
    """Delete datastore for user

    Parameters
    ----------
    name
        Datastore name
    version
        Datastore version
    cluster
        cluster id to operate on

    Raises
    ------
    RuntimeError
        If datastore deletion fails
    """
    client = create_gql_client()
    mutation = """
        mutation (
            $name: String!
            $version: Int!
            $clusterId: String
            ) {
            deleteDatastore (
                properties: {
                        name: $name,
                        version: $version,
                        clusterId: $clusterId
                    }
            ) {
            success
            message
            }
        }
    """
    params = {'name': name, 'version': version, 'clusterId': cluster}
    result = gql_execute(client, mutation, **params)

    if not result['deleteDatastore']['success']:
        message = result['deleteDatastore']['message']
        raise RuntimeError(f'failed to delete datastore {name} with version {version}: {message}')


def create_datastore(name: str, source: str, cluster: Optional[str] = None):
    """Create datastore in Grids
    """
    # Create Grid datastore directly in Grid without uploading, since Grid will
    # handle extraction and creating a optimizted datastore automatically.
    client = create_gql_client()
    mutation = """
        mutation (
            $name: String!
            $source: String
            $clusterId: String
            ) {
            createDatastore (
                properties: {
                        name: $name
                        source: $source
                        clusterId: $clusterId
                    }
            ) {
            success
            message
            datastoreId
            datastoreVersion
            }
        }
    """

    params = {'name': name, 'source': source, 'clusterId': cluster}
    result = gql_execute(client, mutation, **params)
    success = result['createDatastore']['success']
    message = result['createDatastore']['message']
    if not success:
        raise ValueError(f"Unable to create datastore: {message}")

    res = result['createDatastore']
    res['datastoreVersion'] = int(res['datastoreVersion'])
    return res


def get_datastore_upload_multipart_presigned_urls(path: str, datastore_id: str, count: int):
    client = create_gql_client()
    query = """
        query GetMultiPartPresignedUrls (
            $path: String!,
            $datastoreId: ID!,
            $count: Int!
        ) {
            getMultiPartPresignedUrls (
                path: $path,
                datastoreId: $datastoreId,
                count: $count
            ) {
                uploadId
                presignedUrls {
                    url
                    part
                }
            }
        }
    """
    params = {
        'path': path,
        'count': count,
        'datastoreId': datastore_id,
    }
    result = gql_execute(client, query, **params)
    return result['getMultiPartPresignedUrls']


def complete_multipart_datastore_upload(datastore_id: str, upload_id: str, parts: str, path: str, cluster_id: str):
    client = create_gql_client()
    mutation = """
         mutation (
             $datastoreId: ID!
             $uploadId: String!
             $parts: JSONString!
             $path: String!
             $clusterId: String
             ) {
             completeMultipartDatastoreUpload (
                 properties: {
                         datastoreId: $datastoreId
                         uploadId: $uploadId
                         parts: $parts
                         path: $path
                         clusterId: $clusterId
                     }
             ) {
             success
             message
             }
         }
     """
    params = {
        'datastoreId': datastore_id,
        'uploadId': upload_id,
        'parts': parts,
        'path': path,
        'clusterId': cluster_id,
    }
    result = gql_execute(client, mutation, **params)
    success = result['completeMultipartDatastoreUpload']['success']
    message = result['completeMultipartDatastoreUpload']['message']
    if not success:
        raise ValueError(f"Unable to complete multi-part upload: {message}")


def get_user():
    client = create_gql_client()
    query = """
        query {
            getUser {
                isVerified
                completedSignup
                isBlocked
            }
        }
        """
    result = gql_execute(client, query)
    return result["getUser"]
