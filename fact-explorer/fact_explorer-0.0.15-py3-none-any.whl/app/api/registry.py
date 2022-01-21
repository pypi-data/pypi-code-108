from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, Query, Request
from fact_explorer.app.api.constants import API_RESPONSES
from fact_explorer.config import get_logger
from fact_explorer.app.business import registry as business


log = get_logger("api.registry")

router = APIRouter(prefix="/api/registry", responses=API_RESPONSES)


@router.get("/namespaces")
async def namespaces(
    request: Request, with_types: bool = Query(False, alias="with-types")
) -> Union[List[str], Dict[str, List[str]]]:
    """
    Query available namespaces. Can be used to also get event types for all namespaces.

    - `with_types`: also return the types as part of the response. Depending on your
    setup you might be better of with one or two requests here.
    """
    return await business.namespaces(with_types=with_types)


@router.get("/schema")
async def schema(
    request: Request, namespace: str, type: str, version: Optional[int] = None
) -> Dict[str, Any]:
    """
    For a given namespace/type/version tuple, return the stored json schema.

    - `namespace`: The namespace to look in.
    - `type`: The type to look for.
    - `version`: The version of the schema. (Optional - latest by default)
    """
    return await business.schema(namespace=namespace, type=type, version=version)
