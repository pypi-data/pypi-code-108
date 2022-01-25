from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.custom_fields import CustomFields
from ..models.fields import Fields
from ..models.molecule_structure import MoleculeStructure
from ..types import UNSET, Unset

T = TypeVar("T", bound="MoleculeBaseRequest")


@attr.s(auto_attribs=True, repr=False)
class MoleculeBaseRequest:
    """  """

    _aliases: Union[Unset, List[str]] = UNSET
    _author_ids: Union[Unset, List[str]] = UNSET
    _chemical_structure: Union[Unset, MoleculeStructure] = UNSET
    _custom_fields: Union[Unset, CustomFields] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _folder_id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _schema_id: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("aliases={}".format(repr(self._aliases)))
        fields.append("author_ids={}".format(repr(self._author_ids)))
        fields.append("chemical_structure={}".format(repr(self._chemical_structure)))
        fields.append("custom_fields={}".format(repr(self._custom_fields)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        return "MoleculeBaseRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aliases: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aliases, Unset):
            aliases = self._aliases

        author_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._author_ids, Unset):
            author_ids = self._author_ids

        chemical_structure: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._chemical_structure, Unset):
            chemical_structure = self._chemical_structure.to_dict()

        custom_fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._custom_fields, Unset):
            custom_fields = self._custom_fields.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        folder_id = self._folder_id
        name = self._name
        schema_id = self._schema_id

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if aliases is not UNSET:
            field_dict["aliases"] = aliases
        if author_ids is not UNSET:
            field_dict["authorIds"] = author_ids
        if chemical_structure is not UNSET:
            field_dict["chemicalStructure"] = chemical_structure
        if custom_fields is not UNSET:
            field_dict["customFields"] = custom_fields
        if fields is not UNSET:
            field_dict["fields"] = fields
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id
        if name is not UNSET:
            field_dict["name"] = name
        if schema_id is not UNSET:
            field_dict["schemaId"] = schema_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_aliases() -> Union[Unset, List[str]]:
            aliases = cast(List[str], d.pop("aliases"))

            return aliases

        aliases = get_aliases() if "aliases" in d else cast(Union[Unset, List[str]], UNSET)

        def get_author_ids() -> Union[Unset, List[str]]:
            author_ids = cast(List[str], d.pop("authorIds"))

            return author_ids

        author_ids = get_author_ids() if "authorIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_chemical_structure() -> Union[Unset, MoleculeStructure]:
            chemical_structure: Union[Unset, MoleculeStructure] = UNSET
            _chemical_structure = d.pop("chemicalStructure")
            if not isinstance(_chemical_structure, Unset):
                chemical_structure = MoleculeStructure.from_dict(_chemical_structure)

            return chemical_structure

        chemical_structure = (
            get_chemical_structure()
            if "chemicalStructure" in d
            else cast(Union[Unset, MoleculeStructure], UNSET)
        )

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

        def get_folder_id() -> Union[Unset, str]:
            folder_id = d.pop("folderId")
            return folder_id

        folder_id = get_folder_id() if "folderId" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_schema_id() -> Union[Unset, str]:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(Union[Unset, str], UNSET)

        molecule_base_request = cls(
            aliases=aliases,
            author_ids=author_ids,
            chemical_structure=chemical_structure,
            custom_fields=custom_fields,
            fields=fields,
            folder_id=folder_id,
            name=name,
            schema_id=schema_id,
        )

        return molecule_base_request

    @property
    def aliases(self) -> List[str]:
        """ Aliases to add to the Molecule. """
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
    def author_ids(self) -> List[str]:
        """ IDs of users to set as the Molecule's authors. """
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
    def chemical_structure(self) -> MoleculeStructure:
        if isinstance(self._chemical_structure, Unset):
            raise NotPresentError(self, "chemical_structure")
        return self._chemical_structure

    @chemical_structure.setter
    def chemical_structure(self, value: MoleculeStructure) -> None:
        self._chemical_structure = value

    @chemical_structure.deleter
    def chemical_structure(self) -> None:
        self._chemical_structure = UNSET

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
    def folder_id(self) -> str:
        """ID of the folder containing the Molecule."""
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
    def name(self) -> str:
        """Name of the Molecule."""
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
    def schema_id(self) -> str:
        """ID of the Molecule's schema."""
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @schema_id.deleter
    def schema_id(self) -> None:
        self._schema_id = UNSET
