from dataclasses import dataclass
import inspect
from typing import Any, Callable, Dict, List, Optional

from anyscale.client.openapi_client.models.session import Session
from anyscale.sdk.anyscale_client.sdk import AnyscaleSDK


try:
    from ray.client_builder import ClientContext
except ImportError:
    # Import error will be raised in `ClientBuilder.__init__`.
    # Not raising error here to allow `anyscale.connect required_ray_version`
    # to work.
    @dataclass
    class ClientContext:  # type: ignore
        pass


@dataclass
class AnyscaleClientConnectResponse:
    """
    Additional information returned about clusters that were connected from Anyscale.
    """

    cluster_id: str


class AnyscaleClientContext(ClientContext):  # type: ignore
    def __init__(
        self, anyscale_cluster_info: AnyscaleClientConnectResponse, **kwargs: Any,
    ) -> None:
        if _multiclient_supported() and "_context_to_restore" not in kwargs:
            # Set to None for now until multiclient is supported on connect
            kwargs["_context_to_restore"] = None
        super().__init__(**kwargs)
        self.anyscale_cluster_info = anyscale_cluster_info


def _multiclient_supported() -> bool:
    """True if ray version supports multiple clients, False otherwise"""
    _context_params = inspect.signature(ClientContext.__init__).parameters
    return "_context_to_restore" in _context_params


def find_project_id(sdk: AnyscaleSDK, project_name: str) -> Optional[str]:
    """Return id if a project of a given name exists."""
    resp = sdk.search_projects({"name": {"equals": project_name}})
    if len(resp.results) > 0:
        return resp.results[0].id  # type: ignore
    else:
        return None


def get_cluster(
    sdk: AnyscaleSDK, project_id: str, session_name: str
) -> Optional[Session]:
    """Query Anyscale for the given cluster's metadata."""
    results = sdk.search_sessions(
        project_id, {"name": {"equals": session_name}}
    ).results
    cluster_found: Session = None
    for session in results:
        if session.name == session_name:
            cluster_found = session
            break
    return cluster_found


def list_entities(
    list_function: Callable[..., Any],
    container_id: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Any]:
    """Convenience function to automatically handle paging tokens.

    This function repeatedly calls `list_function` with `container_id` until all
    (potentially paged) results are received.
    """
    entities: List[Any] = []
    has_more = True
    paging_token = None
    filters = filters or {}
    while has_more:
        if container_id:
            resp = list_function(
                container_id, count=50, paging_token=paging_token, **filters
            )
        else:
            resp = list_function(count=50, paging_token=paging_token, **filters)
        entities.extend(resp.results)
        paging_token = resp.metadata.next_paging_token
        has_more = paging_token is not None
    return entities
