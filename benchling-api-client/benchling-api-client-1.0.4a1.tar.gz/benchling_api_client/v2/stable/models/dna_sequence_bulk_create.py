from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.custom_fields import CustomFields
from ..models.dna_annotation import DnaAnnotation
from ..models.fields import Fields
from ..models.naming_strategy import NamingStrategy
from ..models.primer import Primer
from ..models.translation import Translation
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaSequenceBulkCreate")


@attr.s(auto_attribs=True, repr=False)
class DnaSequenceBulkCreate:
    """  """

    _entity_registry_id: Union[Unset, str] = UNSET
    _folder_id: Union[Unset, str] = UNSET
    _naming_strategy: Union[Unset, NamingStrategy] = UNSET
    _registry_id: Union[Unset, str] = UNSET
    _aliases: Union[Unset, List[str]] = UNSET
    _annotations: Union[Unset, List[DnaAnnotation]] = UNSET
    _author_ids: Union[Unset, List[str]] = UNSET
    _bases: Union[Unset, str] = UNSET
    _custom_fields: Union[Unset, CustomFields] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _is_circular: Union[Unset, bool] = UNSET
    _name: Union[Unset, str] = UNSET
    _primers: Union[Unset, List[Primer]] = UNSET
    _schema_id: Union[Unset, str] = UNSET
    _translations: Union[Unset, List[Translation]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entity_registry_id={}".format(repr(self._entity_registry_id)))
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("naming_strategy={}".format(repr(self._naming_strategy)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("aliases={}".format(repr(self._aliases)))
        fields.append("annotations={}".format(repr(self._annotations)))
        fields.append("author_ids={}".format(repr(self._author_ids)))
        fields.append("bases={}".format(repr(self._bases)))
        fields.append("custom_fields={}".format(repr(self._custom_fields)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("is_circular={}".format(repr(self._is_circular)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("primers={}".format(repr(self._primers)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("translations={}".format(repr(self._translations)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaSequenceBulkCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_registry_id = self._entity_registry_id
        folder_id = self._folder_id
        naming_strategy: Union[Unset, int] = UNSET
        if not isinstance(self._naming_strategy, Unset):
            naming_strategy = self._naming_strategy.value

        registry_id = self._registry_id
        aliases: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aliases, Unset):
            aliases = self._aliases

        annotations: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._annotations, Unset):
            annotations = []
            for annotations_item_data in self._annotations:
                annotations_item = annotations_item_data.to_dict()

                annotations.append(annotations_item)

        author_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._author_ids, Unset):
            author_ids = self._author_ids

        bases = self._bases
        custom_fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._custom_fields, Unset):
            custom_fields = self._custom_fields.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        is_circular = self._is_circular
        name = self._name
        primers: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._primers, Unset):
            primers = []
            for primers_item_data in self._primers:
                primers_item = primers_item_data.to_dict()

                primers.append(primers_item)

        schema_id = self._schema_id
        translations: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._translations, Unset):
            translations = []
            for translations_item_data in self._translations:
                translations_item = translations_item_data.to_dict()

                translations.append(translations_item)

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
        if aliases is not UNSET:
            field_dict["aliases"] = aliases
        if annotations is not UNSET:
            field_dict["annotations"] = annotations
        if author_ids is not UNSET:
            field_dict["authorIds"] = author_ids
        if bases is not UNSET:
            field_dict["bases"] = bases
        if custom_fields is not UNSET:
            field_dict["customFields"] = custom_fields
        if fields is not UNSET:
            field_dict["fields"] = fields
        if is_circular is not UNSET:
            field_dict["isCircular"] = is_circular
        if name is not UNSET:
            field_dict["name"] = name
        if primers is not UNSET:
            field_dict["primers"] = primers
        if schema_id is not UNSET:
            field_dict["schemaId"] = schema_id
        if translations is not UNSET:
            field_dict["translations"] = translations

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

        def get_aliases() -> Union[Unset, List[str]]:
            aliases = cast(List[str], d.pop("aliases"))

            return aliases

        aliases = get_aliases() if "aliases" in d else cast(Union[Unset, List[str]], UNSET)

        def get_annotations() -> Union[Unset, List[DnaAnnotation]]:
            annotations = []
            _annotations = d.pop("annotations")
            for annotations_item_data in _annotations or []:
                annotations_item = DnaAnnotation.from_dict(annotations_item_data)

                annotations.append(annotations_item)

            return annotations

        annotations = (
            get_annotations() if "annotations" in d else cast(Union[Unset, List[DnaAnnotation]], UNSET)
        )

        def get_author_ids() -> Union[Unset, List[str]]:
            author_ids = cast(List[str], d.pop("authorIds"))

            return author_ids

        author_ids = get_author_ids() if "authorIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_bases() -> Union[Unset, str]:
            bases = d.pop("bases")
            return bases

        bases = get_bases() if "bases" in d else cast(Union[Unset, str], UNSET)

        def get_custom_fields() -> Union[Unset, CustomFields]:
            custom_fields: Union[Unset, CustomFields] = UNSET
            _custom_fields = d.pop("customFields")
            if not isinstance(_custom_fields, Unset):
                custom_fields = CustomFields.from_dict(_custom_fields)

            return custom_fields

        custom_fields = (
            get_custom_fields() if "customFields" in d else cast(Union[Unset, CustomFields], UNSET)
        )

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_is_circular() -> Union[Unset, bool]:
            is_circular = d.pop("isCircular")
            return is_circular

        is_circular = get_is_circular() if "isCircular" in d else cast(Union[Unset, bool], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_primers() -> Union[Unset, List[Primer]]:
            primers = []
            _primers = d.pop("primers")
            for primers_item_data in _primers or []:
                primers_item = Primer.from_dict(primers_item_data)

                primers.append(primers_item)

            return primers

        primers = get_primers() if "primers" in d else cast(Union[Unset, List[Primer]], UNSET)

        def get_schema_id() -> Union[Unset, str]:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(Union[Unset, str], UNSET)

        def get_translations() -> Union[Unset, List[Translation]]:
            translations = []
            _translations = d.pop("translations")
            for translations_item_data in _translations or []:
                translations_item = Translation.from_dict(translations_item_data)

                translations.append(translations_item)

            return translations

        translations = (
            get_translations() if "translations" in d else cast(Union[Unset, List[Translation]], UNSET)
        )

        dna_sequence_bulk_create = cls(
            entity_registry_id=entity_registry_id,
            folder_id=folder_id,
            naming_strategy=naming_strategy,
            registry_id=registry_id,
            aliases=aliases,
            annotations=annotations,
            author_ids=author_ids,
            bases=bases,
            custom_fields=custom_fields,
            fields=fields,
            is_circular=is_circular,
            name=name,
            primers=primers,
            schema_id=schema_id,
            translations=translations,
        )

        dna_sequence_bulk_create.additional_properties = d
        return dna_sequence_bulk_create

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
        """ID of the folder containing the DNA sequence."""
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

    @property
    def aliases(self) -> List[str]:
        """ Aliases to add to the DNA sequence """
        if isinstance(self._aliases, Unset):
            raise NotPresentError(self, "aliases")
        return self._aliases

    @aliases.setter
    def aliases(self, value: List[str]) -> None:
        self._aliases = value

    @aliases.deleter
    def aliases(self) -> None:
        self._aliases = UNSET

    @property
    def annotations(self) -> List[DnaAnnotation]:
        """Annotations to create on the DNA sequence."""
        if isinstance(self._annotations, Unset):
            raise NotPresentError(self, "annotations")
        return self._annotations

    @annotations.setter
    def annotations(self, value: List[DnaAnnotation]) -> None:
        self._annotations = value

    @annotations.deleter
    def annotations(self) -> None:
        self._annotations = UNSET

    @property
    def author_ids(self) -> List[str]:
        """ IDs of users to set as the DNA sequence's authors. """
        if isinstance(self._author_ids, Unset):
            raise NotPresentError(self, "author_ids")
        return self._author_ids

    @author_ids.setter
    def author_ids(self, value: List[str]) -> None:
        self._author_ids = value

    @author_ids.deleter
    def author_ids(self) -> None:
        self._author_ids = UNSET

    @property
    def bases(self) -> str:
        """Base pairs for the DNA sequence."""
        if isinstance(self._bases, Unset):
            raise NotPresentError(self, "bases")
        return self._bases

    @bases.setter
    def bases(self, value: str) -> None:
        self._bases = value

    @bases.deleter
    def bases(self) -> None:
        self._bases = UNSET

    @property
    def custom_fields(self) -> CustomFields:
        if isinstance(self._custom_fields, Unset):
            raise NotPresentError(self, "custom_fields")
        return self._custom_fields

    @custom_fields.setter
    def custom_fields(self, value: CustomFields) -> None:
        self._custom_fields = value

    @custom_fields.deleter
    def custom_fields(self) -> None:
        self._custom_fields = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET

    @property
    def is_circular(self) -> bool:
        """Whether the DNA sequence is circular or linear."""
        if isinstance(self._is_circular, Unset):
            raise NotPresentError(self, "is_circular")
        return self._is_circular

    @is_circular.setter
    def is_circular(self, value: bool) -> None:
        self._is_circular = value

    @is_circular.deleter
    def is_circular(self) -> None:
        self._is_circular = UNSET

    @property
    def name(self) -> str:
        """Name of the DNA sequence."""
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def primers(self) -> List[Primer]:
        if isinstance(self._primers, Unset):
            raise NotPresentError(self, "primers")
        return self._primers

    @primers.setter
    def primers(self, value: List[Primer]) -> None:
        self._primers = value

    @primers.deleter
    def primers(self) -> None:
        self._primers = UNSET

    @property
    def schema_id(self) -> str:
        """ID of the DNA sequence's schema."""
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @schema_id.deleter
    def schema_id(self) -> None:
        self._schema_id = UNSET

    @property
    def translations(self) -> List[Translation]:
        """Translations to create on the DNA sequence."""
        if isinstance(self._translations, Unset):
            raise NotPresentError(self, "translations")
        return self._translations

    @translations.setter
    def translations(self, value: List[Translation]) -> None:
        self._translations = value

    @translations.deleter
    def translations(self) -> None:
        self._translations = UNSET
