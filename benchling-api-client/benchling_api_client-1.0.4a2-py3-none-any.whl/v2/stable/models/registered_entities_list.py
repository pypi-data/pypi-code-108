from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.aa_sequence_with_entity_type import AaSequenceWithEntityType
from ..models.custom_entity_with_entity_type import CustomEntityWithEntityType
from ..models.dna_oligo_with_entity_type import DnaOligoWithEntityType
from ..models.dna_sequence_with_entity_type import DnaSequenceWithEntityType
from ..models.mixture_with_entity_type import MixtureWithEntityType
from ..models.rna_oligo_with_entity_type import RnaOligoWithEntityType
from ..types import UNSET, Unset

T = TypeVar("T", bound="RegisteredEntitiesList")


@attr.s(auto_attribs=True, repr=False)
class RegisteredEntitiesList:
    """  """

    _entities: Union[
        Unset,
        List[
            Union[
                DnaSequenceWithEntityType,
                CustomEntityWithEntityType,
                AaSequenceWithEntityType,
                MixtureWithEntityType,
                DnaOligoWithEntityType,
                RnaOligoWithEntityType,
                UnknownType,
            ]
        ],
    ] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entities={}".format(repr(self._entities)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RegisteredEntitiesList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entities: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._entities, Unset):
            entities = []
            for entities_item_data in self._entities:
                if isinstance(entities_item_data, UnknownType):
                    entities_item = entities_item_data.value
                elif isinstance(entities_item_data, DnaSequenceWithEntityType):
                    entities_item = entities_item_data.to_dict()

                elif isinstance(entities_item_data, CustomEntityWithEntityType):
                    entities_item = entities_item_data.to_dict()

                elif isinstance(entities_item_data, AaSequenceWithEntityType):
                    entities_item = entities_item_data.to_dict()

                elif isinstance(entities_item_data, MixtureWithEntityType):
                    entities_item = entities_item_data.to_dict()

                elif isinstance(entities_item_data, DnaOligoWithEntityType):
                    entities_item = entities_item_data.to_dict()

                else:
                    entities_item = entities_item_data.to_dict()

                entities.append(entities_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entities is not UNSET:
            field_dict["entities"] = entities

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entities() -> Union[
            Unset,
            List[
                Union[
                    DnaSequenceWithEntityType,
                    CustomEntityWithEntityType,
                    AaSequenceWithEntityType,
                    MixtureWithEntityType,
                    DnaOligoWithEntityType,
                    RnaOligoWithEntityType,
                    UnknownType,
                ]
            ],
        ]:
            entities = []
            _entities = d.pop("entities")
            for entities_item_data in _entities or []:

                def _parse_entities_item(
                    data: Union[Dict[str, Any]]
                ) -> Union[
                    DnaSequenceWithEntityType,
                    CustomEntityWithEntityType,
                    AaSequenceWithEntityType,
                    MixtureWithEntityType,
                    DnaOligoWithEntityType,
                    RnaOligoWithEntityType,
                    UnknownType,
                ]:
                    entities_item: Union[
                        DnaSequenceWithEntityType,
                        CustomEntityWithEntityType,
                        AaSequenceWithEntityType,
                        MixtureWithEntityType,
                        DnaOligoWithEntityType,
                        RnaOligoWithEntityType,
                        UnknownType,
                    ]
                    discriminator_value: str = cast(str, data.get("entityType"))
                    if discriminator_value is not None:
                        if discriminator_value == "dna_sequence":
                            entities_item = DnaSequenceWithEntityType.from_dict(data)

                            return entities_item
                        if discriminator_value == "custom_entity":
                            entities_item = CustomEntityWithEntityType.from_dict(data)

                            return entities_item
                        if discriminator_value == "aa_sequence":
                            entities_item = AaSequenceWithEntityType.from_dict(data)

                            return entities_item
                        if discriminator_value == "mixture":
                            entities_item = MixtureWithEntityType.from_dict(data)

                            return entities_item
                        if discriminator_value == "dna_oligo":
                            entities_item = DnaOligoWithEntityType.from_dict(data)

                            return entities_item
                        if discriminator_value == "rna_oligo":
                            entities_item = RnaOligoWithEntityType.from_dict(data)

                            return entities_item

                        return UnknownType(value=data)
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        entities_item = DnaSequenceWithEntityType.from_dict(data)

                        return entities_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        entities_item = CustomEntityWithEntityType.from_dict(data)

                        return entities_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        entities_item = AaSequenceWithEntityType.from_dict(data)

                        return entities_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        entities_item = MixtureWithEntityType.from_dict(data)

                        return entities_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        entities_item = DnaOligoWithEntityType.from_dict(data)

                        return entities_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        entities_item = RnaOligoWithEntityType.from_dict(data)

                        return entities_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                entities_item = _parse_entities_item(entities_item_data)

                entities.append(entities_item)

            return entities

        entities = (
            get_entities()
            if "entities" in d
            else cast(
                Union[
                    Unset,
                    List[
                        Union[
                            DnaSequenceWithEntityType,
                            CustomEntityWithEntityType,
                            AaSequenceWithEntityType,
                            MixtureWithEntityType,
                            DnaOligoWithEntityType,
                            RnaOligoWithEntityType,
                            UnknownType,
                        ]
                    ],
                ],
                UNSET,
            )
        )

        registered_entities_list = cls(
            entities=entities,
        )

        registered_entities_list.additional_properties = d
        return registered_entities_list

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def entities(
        self,
    ) -> List[
        Union[
            DnaSequenceWithEntityType,
            CustomEntityWithEntityType,
            AaSequenceWithEntityType,
            MixtureWithEntityType,
            DnaOligoWithEntityType,
            RnaOligoWithEntityType,
            UnknownType,
        ]
    ]:
        if isinstance(self._entities, Unset):
            raise NotPresentError(self, "entities")
        return self._entities

    @entities.setter
    def entities(
        self,
        value: List[
            Union[
                DnaSequenceWithEntityType,
                CustomEntityWithEntityType,
                AaSequenceWithEntityType,
                MixtureWithEntityType,
                DnaOligoWithEntityType,
                RnaOligoWithEntityType,
                UnknownType,
            ]
        ],
    ) -> None:
        self._entities = value

    @entities.deleter
    def entities(self) -> None:
        self._entities = UNSET
