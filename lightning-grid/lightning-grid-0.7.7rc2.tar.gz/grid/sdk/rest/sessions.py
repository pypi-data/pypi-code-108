from typing import Dict, List, Optional

from grid.openapi import (
    Body1,
    Externalv1Session,
    V1CreateSessionRequest,
    V1CreateSessionResponse,
    V1DatastoreInput,
    V1DeleteSessionResponse,
    V1GetSessionResponse,
    V1ListSessionsResponse,
    V1Resources,
    V1SessionSpec,
    V1SessionState,
    V1UpdateSessionResponse,
)
from grid.sdk.datastores import Datastore
from grid.sdk.rest.client import GridRestClient
from grid.sdk.rest.datastores import datastore_dsn_from_id
from grid.sdk.rest.exceptions import throw_with_message


@throw_with_message
def get_session_from_name(c: GridRestClient, name: str, cluster_id: str) -> Externalv1Session:
    """Find the id of a session with some name on a cluster.

    Parameters
    ----------
    c
        Client
    name
        the name of the session to find the ID of
    cluster_id
        which cluster should be used to find the datastore in.

    Returns
    -------
    str
       The ID of the session.
    """
    sessions: V1ListSessionsResponse = c.session_service_list_sessions(
        cluster_id=cluster_id, phase_in=[V1SessionState.RUNNING, V1SessionState.PAUSED, V1SessionState.PENDING]
    )
    for session in sessions.sessions:
        session: Externalv1Session
        if session.name == name:
            return session

    raise KeyError(f"could not find session with name {name} in cluster {cluster_id}")


@throw_with_message
def list_sessions(c: GridRestClient,
                  cluster_id: Optional[str] = None,
                  user_ids: Optional[List[str]] = None) -> List[Externalv1Session]:
    kwargs = {}
    if cluster_id is not None:
        kwargs['cluster_id'] = cluster_id
    if user_ids is not None:
        kwargs['user_ids'] = user_ids
    kwargs['phase_not_in'] = [V1SessionState.DELETED]

    resp: V1ListSessionsResponse = c.session_service_list_sessions(**kwargs)
    return resp.sessions


@throw_with_message
def get_session_from_id(c: GridRestClient, session_id: str) -> V1GetSessionResponse:
    return c.session_service_get_session(id=session_id)


@throw_with_message
def create_session(
    c: GridRestClient,
    name: str,
    instance_type: str,
    cluster_id: Optional[str] = None,
    datastores: Optional[Dict[str, str]] = None,  # datastore_id: mount_path
    disk_size_gb: str = '200',
    use_spot: bool = False
) -> V1CreateSessionResponse:
    """Create a session on the grid platform.

    Parameters
    ----------
    c
        API client
    name
        human readable name of the session which is created
    instance_type
        cloud provider instance type used to start the session on.
    cluster_id
        cluster ID to start the session on
    disk_size_gb
        The size of the disk to use.
    datastores
        mapping of datastore id to datastore mount dir
    use_spot
        if we should use a spot instance or not.

    Returns
    -------
    str
        ID of the session which was created.
    """
    datastore_mounts = None
    if datastores:
        datastore_mounts = [
            V1DatastoreInput(dsn=datastore_dsn_from_id(id=key), mount_path=value) for key, value in datastores.items()
        ]

    request = V1CreateSessionRequest(
        name=name,
        spec=V1SessionSpec(
            cluster_id=cluster_id,
            use_spot=use_spot,
            desired_state=V1SessionState.RUNNING,
            instance_type=instance_type,
            datastores=datastore_mounts,
            resources=V1Resources(storage_gb=disk_size_gb, )
        )
    )
    resp = c.session_service_create_session(request)
    return resp


@throw_with_message
def pause_session(c: GridRestClient, session_id: str, cluster_id: Optional[str] = None) -> V1UpdateSessionResponse:
    """Pause a session with a given name.

    Parameters
    ----------
    c
        Open API client
    session_id
        session id
    cluster_id
        cluster containing the session which will be paused

    Returns
    -------
    str
        ID of the session which is paused.
    """
    session = get_session_from_id(c=c, session_id=session_id)
    session.spec.desired_state = V1SessionState.PAUSED
    resp: V1UpdateSessionResponse = c.session_service_update_session(
        id=session.id, body=Body1(name=session.name, spec=session.spec)
    )
    return resp


@throw_with_message
def delete_session(c: GridRestClient, session_id: str, cluster_id: Optional[str] = None) -> V1DeleteSessionResponse:
    """Delete a session with a given name.

    Parameters
    ----------
    c
        Open API client
    session_id
        id of the session to delete
    cluster_id
        cluster containing the session which will be deleted

    Returns
    -------
    str
        ID of the session which is deleted.
    """
    return c.session_service_delete_session(id=session_id)


@throw_with_message
def resume_session(c: GridRestClient, session_id: str, cluster_id: Optional[str] = None) -> V1UpdateSessionResponse:
    """Resumes a session with a given name.

    Parameters
    ----------
    c
        Open API client
    session_id
        id of the session to pause
    cluster_id
        cluster containing the session which will be resumed

    Returns
    -------
    V1UpdateSessionResponse
        session which is resumed
    """
    session = get_session_from_id(c, session_id=session_id)

    spec: V1SessionSpec = session.spec
    spec.desired_state = V1SessionState.RUNNING
    session.spec = spec
    resp: V1UpdateSessionResponse = c.session_service_update_session(
        id=session.id, body=Body1(name=session.name, spec=spec)
    )
    return resp


@throw_with_message
def change_session_instance_type(
    c: GridRestClient,
    session_id: str,
    instance_type,
    use_spot: Optional[bool] = None,
    cluster_id: Optional[str] = None
) -> V1UpdateSessionResponse:
    """Change the instance type of a session.

    Parameters
    ----------
    c
        Open API Client
    session_id
        name of the session to alter
    instance_type
        new instance type to use for the session
    use_spot
        if true, use interuptable spot instances (which come at a steap discount,
        but which can be interrupted and shut down at any point in time depending
        on cloud provider instance type demand). If false, use an on-demand instance.

        By default this value is None, indicating that no change will be made to the
        current configuratoin.
    cluster_id
        cluster ID of the session to change the instance type of

    Returns
    -------
    V1UpdateSessionResponse
        response from the server
    """
    session = get_session_from_id(c, session_id=session_id)
    session.spec.instance_type = instance_type
    if use_spot is not None:
        session.spec.use_spot = use_spot

    result = c.session_service_update_session(
        id=session.id,
        body=Body1(name=session.name, spec=session.spec),
    )
    return result
