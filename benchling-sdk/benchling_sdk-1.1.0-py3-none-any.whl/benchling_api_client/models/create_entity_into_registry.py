from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.naming_strategy import NamingStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateEntityIntoRegistry")


@attr.s(auto_attribs=True, repr=False)
class CreateEntityIntoRegistry:
    """  """

    _entity_registry_id: Union[Unset, str] = UNSET
    _folder_id: Union[Unset, str] = UNSET
    _naming_strategy: Union[Unset, NamingStrategy] = UNSET
    _registry_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entity_registry_id={}".format(repr(self._entity_registry_id)))
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("naming_strategy={}".format(repr(self._naming_strategy)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "CreateEntityIntoRegistry({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_registry_id = self._entity_registry_id
        folder_id = self._folder_id
        naming_strategy: Union[Unset, int] = UNSET
        if not isinstance(self._naming_strategy, Unset):
            naming_strategy = self._naming_strategy.value

        registry_id = self._registry_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entity_registry_id is not UNSET:
            field_dict["entityRegistryId"] = entity_registry_id
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id
        if naming_strategy is not UNSET:
            field_dict["namingStrategy"] = naming_strategy
        if registry_id is not UNSET:
            field_dict["registryId"] = registry_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entity_registry_id() -> Union[Unset, str]:
            entity_registry_id = d.pop("entityRegistryId")
            return entity_registry_id

        entity_registry_id = (
            get_entity_registry_id() if "entityRegistryId" in d else cast(Union[Unset, str], UNSET)
        )

        def get_folder_id() -> Union[Unset, str]:
            folder_id = d.pop("folderId")
            return folder_id

        folder_id = get_folder_id() if "folderId" in d else cast(Union[Unset, str], UNSET)

        def get_naming_strategy() -> Union[Unset, NamingStrategy]:
            naming_strategy = None
            _naming_strategy = d.pop("namingStrategy")
            if _naming_strategy is not None and _naming_strategy is not UNSET:
                try:
                    naming_strategy = NamingStrategy(_naming_strategy)
                except ValueError:
                    naming_strategy = NamingStrategy.of_unknown(_naming_strategy)

            return naming_strategy

        naming_strategy = (
            get_naming_strategy() if "namingStrategy" in d else cast(Union[Unset, NamingStrategy], UNSET)
        )

        def get_registry_id() -> Union[Unset, str]:
            registry_id = d.pop("registryId")
            return registry_id

        registry_id = get_registry_id() if "registryId" in d else cast(Union[Unset, str], UNSET)

        create_entity_into_registry = cls(
            entity_registry_id=entity_registry_id,
            folder_id=folder_id,
            naming_strategy=naming_strategy,
            registry_id=registry_id,
        )

        create_entity_into_registry.additional_properties = d
        return create_entity_into_registry

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
    def entity_registry_id(self) -> str:
        """Entity registry ID to set for the registered entity. Cannot specify both entityRegistryId and namingStrategy at the same time."""
        if isinstance(self._entity_registry_id, Unset):
            raise NotPresentError(self, "entity_registry_id")
        return self._entity_registry_id

    @entity_registry_id.setter
    def entity_registry_id(self, value: str) -> None:
        self._entity_registry_id = value

    @entity_registry_id.deleter
    def entity_registry_id(self) -> None:
        self._entity_registry_id = UNSET

    @property
    def folder_id(self) -> str:
        """ ID of the folder containing the entity. Can be left empty when registryId is present. """
        if isinstance(self._folder_id, Unset):
            raise NotPresentError(self, "folder_id")
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: str) -> None:
        self._folder_id = value

    @folder_id.deleter
    def folder_id(self) -> None:
        self._folder_id = UNSET

    @property
    def naming_strategy(self) -> NamingStrategy:
        """Specifies the behavior for automatically generated names when registering an entity.
        - NEW_IDS: Generate new registry IDs
        - IDS_FROM_NAMES: Generate registry IDs based on entity names
        - DELETE_NAMES: Generate new registry IDs and replace name with registry ID
        - SET_FROM_NAME_PARTS: Generate new registry IDs, rename according to name template, and keep old name as alias
        - REPLACE_NAMES_FROM_PARTS: Generate new registry IDs, and replace name according to name template
        - KEEP_NAMES: Keep existing entity names as registry IDs
        - REPLACE_ID_AND_NAME_FROM_PARTS: Generate registry IDs and names according to name template
        """
        if isinstance(self._naming_strategy, Unset):
            raise NotPresentError(self, "naming_strategy")
        return self._naming_strategy

    @naming_strategy.setter
    def naming_strategy(self, value: NamingStrategy) -> None:
        self._naming_strategy = value

    @naming_strategy.deleter
    def naming_strategy(self) -> None:
        self._naming_strategy = UNSET

    @property
    def registry_id(self) -> str:
        """Registry ID into which entity should be registered. this is the ID of the registry which was configured for a particular organization
        To get available registryIds, use the [/registries endpoint](#/Registry/listRegistries)

        Required in order for entities to be created directly in the registry.
        """
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: str) -> None:
        self._registry_id = value

    @registry_id.deleter
    def registry_id(self) -> None:
        self._registry_id = UNSET
