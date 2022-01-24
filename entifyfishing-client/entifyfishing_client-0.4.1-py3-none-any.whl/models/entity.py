from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.bounding_box import BoundingBox
from ..types import UNSET, Unset

T = TypeVar("T", bound="Entity")


@attr.s(auto_attribs=True)
class Entity:
    """ """

    offset_start: int
    offset_end: int
    pos: Union[Unset, List[BoundingBox]] = UNSET
    raw_name: Union[Unset, str] = UNSET
    confidence_score: Union[Unset, float] = UNSET
    wikipedia_external_ref: Union[Unset, int] = UNSET
    wikidata_id: Union[Unset, str] = UNSET
    domains: Union[Unset, List[str]] = UNSET
    type: Union[Unset, str] = UNSET
    sense: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        offset_start = self.offset_start
        offset_end = self.offset_end
        pos: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.pos, Unset):
            pos = []
            for pos_item_data in self.pos:
                pos_item = pos_item_data.to_dict()

                pos.append(pos_item)

        raw_name = self.raw_name
        confidence_score = self.confidence_score
        wikipedia_external_ref = self.wikipedia_external_ref
        wikidata_id = self.wikidata_id
        domains: Union[Unset, List[str]] = UNSET
        if not isinstance(self.domains, Unset):
            domains = self.domains

        type = self.type
        sense = self.sense

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "offsetStart": offset_start,
                "offsetEnd": offset_end,
            }
        )
        if pos is not UNSET:
            field_dict["pos"] = pos
        if raw_name is not UNSET:
            field_dict["rawName"] = raw_name
        if confidence_score is not UNSET:
            field_dict["confidence_score"] = confidence_score
        if wikipedia_external_ref is not UNSET:
            field_dict["wikipediaExternalRef"] = wikipedia_external_ref
        if wikidata_id is not UNSET:
            field_dict["wikidataId"] = wikidata_id
        if domains is not UNSET:
            field_dict["domains"] = domains
        if type is not UNSET:
            field_dict["type"] = type
        if sense is not UNSET:
            field_dict["sense"] = sense

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        offset_start = d.pop("offsetStart")

        offset_end = d.pop("offsetEnd")

        pos = []
        _pos = d.pop("pos", UNSET)
        for pos_item_data in _pos or []:
            pos_item = BoundingBox.from_dict(pos_item_data)

            pos.append(pos_item)

        raw_name = d.pop("rawName", UNSET)

        confidence_score = d.pop("confidence_score", UNSET)

        wikipedia_external_ref = d.pop("wikipediaExternalRef", UNSET)

        wikidata_id = d.pop("wikidataId", UNSET)

        domains = cast(List[str], d.pop("domains", UNSET))

        type = d.pop("type", UNSET)

        sense = d.pop("sense", UNSET)

        entity = cls(
            offset_start=offset_start,
            offset_end=offset_end,
            pos=pos,
            raw_name=raw_name,
            confidence_score=confidence_score,
            wikipedia_external_ref=wikipedia_external_ref,
            wikidata_id=wikidata_id,
            domains=domains,
            type=type,
            sense=sense,
        )

        return entity
