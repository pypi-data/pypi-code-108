from typing import List, Optional

from cognite.well_model.client.utils.exceptions import CogniteInvalidInput
from cognite.well_model.models import Identifier, IdentifierItems


def identifier_list(
    asset_external_ids: Optional[List[str]] = None, matching_ids: Optional[List[str]] = None
) -> Optional[List[Identifier]]:
    if asset_external_ids is None and matching_ids is None:
        return None

    identifiers = []
    for asset_external_id in asset_external_ids or []:
        identifiers.append(Identifier(asset_external_id=asset_external_id))
    for matching_id in matching_ids or []:
        identifiers.append(Identifier(matching_id=matching_id))
    return identifiers


def create_identifier(external_id: Optional[str], matching_id: Optional[str]):
    if external_id is None and matching_id is None:
        raise CogniteInvalidInput("One of external_id or matching_id must be set")
    if external_id is not None and matching_id is not None:
        raise CogniteInvalidInput("Only one of external_id and matching_id must be set")
    return Identifier(asset_external_id=external_id, matching_id=matching_id)


def identifier_items(
    asset_external_ids: Optional[List[str]] = None, matching_ids: Optional[List[str]] = None
) -> IdentifierItems:
    identifiers = identifier_list(asset_external_ids, matching_ids)
    if not identifiers:
        raise CogniteInvalidInput("Identifier list can't be empty")
    return IdentifierItems(items=identifiers)


def identifier_items_single(
    asset_external_id: Optional[str] = None, matching_id: Optional[str] = None
) -> IdentifierItems:
    return IdentifierItems(items=[create_identifier(asset_external_id, matching_id)])
