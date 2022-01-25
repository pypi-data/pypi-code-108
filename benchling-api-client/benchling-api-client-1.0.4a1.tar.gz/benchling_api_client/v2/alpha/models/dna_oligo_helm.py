import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.archive_record import ArchiveRecord
from ..models.custom_fields import CustomFields
from ..models.fields import Fields
from ..models.oligo_nucleotide_type import OligoNucleotideType
from ..models.registration_origin import RegistrationOrigin
from ..models.schema_summary import SchemaSummary
from ..models.user_summary import UserSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaOligoHelm")


@attr.s(auto_attribs=True, repr=False)
class DnaOligoHelm:
    """  """

    _helm: Union[Unset, str] = UNSET
    _api_url: Union[Unset, str] = UNSET
    _bases: Union[Unset, str] = UNSET
    _aliases: Union[Unset, List[str]] = UNSET
    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    _created_at: Union[Unset, datetime.datetime] = UNSET
    _creator: Union[Unset, UserSummary] = UNSET
    _custom_fields: Union[Unset, CustomFields] = UNSET
    _entity_registry_id: Union[Unset, None, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _folder_id: Union[Unset, None, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _length: Union[Unset, int] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _name: Union[Unset, str] = UNSET
    _nucleotide_type: Union[Unset, OligoNucleotideType] = UNSET
    _registration_origin: Union[Unset, None, RegistrationOrigin] = UNSET
    _registry_id: Union[Unset, None, str] = UNSET
    _schema: Union[Unset, None, SchemaSummary] = UNSET
    _web_url: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("helm={}".format(repr(self._helm)))
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("bases={}".format(repr(self._bases)))
        fields.append("aliases={}".format(repr(self._aliases)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("custom_fields={}".format(repr(self._custom_fields)))
        fields.append("entity_registry_id={}".format(repr(self._entity_registry_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("length={}".format(repr(self._length)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("nucleotide_type={}".format(repr(self._nucleotide_type)))
        fields.append("registration_origin={}".format(repr(self._registration_origin)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaOligoHelm({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        helm = self._helm
        api_url = self._api_url
        bases = self._bases
        aliases: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aliases, Unset):
            aliases = self._aliases

        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        custom_fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._custom_fields, Unset):
            custom_fields = self._custom_fields.to_dict()

        entity_registry_id = self._entity_registry_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        folder_id = self._folder_id
        id = self._id
        length = self._length
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        name = self._name
        nucleotide_type: Union[Unset, int] = UNSET
        if not isinstance(self._nucleotide_type, Unset):
            nucleotide_type = self._nucleotide_type.value

        registration_origin: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._registration_origin, Unset):
            registration_origin = self._registration_origin.to_dict() if self._registration_origin else None

        registry_id = self._registry_id
        schema: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._schema, Unset):
            schema = self._schema.to_dict() if self._schema else None

        web_url = self._web_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if helm is not UNSET:
            field_dict["helm"] = helm
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if bases is not UNSET:
            field_dict["bases"] = bases
        if aliases is not UNSET:
            field_dict["aliases"] = aliases
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if creator is not UNSET:
            field_dict["creator"] = creator
        if custom_fields is not UNSET:
            field_dict["customFields"] = custom_fields
        if entity_registry_id is not UNSET:
            field_dict["entityRegistryId"] = entity_registry_id
        if fields is not UNSET:
            field_dict["fields"] = fields
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id
        if id is not UNSET:
            field_dict["id"] = id
        if length is not UNSET:
            field_dict["length"] = length
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if name is not UNSET:
            field_dict["name"] = name
        if nucleotide_type is not UNSET:
            field_dict["nucleotideType"] = nucleotide_type
        if registration_origin is not UNSET:
            field_dict["registrationOrigin"] = registration_origin
        if registry_id is not UNSET:
            field_dict["registryId"] = registry_id
        if schema is not UNSET:
            field_dict["schema"] = schema
        if web_url is not UNSET:
            field_dict["webURL"] = web_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_helm() -> Union[Unset, str]:
            helm = d.pop("helm")
            return helm

        helm = get_helm() if "helm" in d else cast(Union[Unset, str], UNSET)

        def get_api_url() -> Union[Unset, str]:
            api_url = d.pop("apiURL")
            return api_url

        api_url = get_api_url() if "apiURL" in d else cast(Union[Unset, str], UNSET)

        def get_bases() -> Union[Unset, str]:
            bases = d.pop("bases")
            return bases

        bases = get_bases() if "bases" in d else cast(Union[Unset, str], UNSET)

        def get_aliases() -> Union[Unset, List[str]]:
            aliases = cast(List[str], d.pop("aliases"))

            return aliases

        aliases = get_aliases() if "aliases" in d else cast(Union[Unset, List[str]], UNSET)

        def get_archive_record() -> Union[Unset, None, ArchiveRecord]:
            archive_record = None
            _archive_record = d.pop("archiveRecord")
            if _archive_record is not None and not isinstance(_archive_record, Unset):
                archive_record = ArchiveRecord.from_dict(_archive_record)

            return archive_record

        archive_record = (
            get_archive_record() if "archiveRecord" in d else cast(Union[Unset, None, ArchiveRecord], UNSET)
        )

        def get_created_at() -> Union[Unset, datetime.datetime]:
            created_at: Union[Unset, datetime.datetime] = UNSET
            _created_at = d.pop("createdAt")
            if _created_at is not None and not isinstance(_created_at, Unset):
                created_at = isoparse(cast(str, _created_at))

            return created_at

        created_at = get_created_at() if "createdAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_creator() -> Union[Unset, UserSummary]:
            creator: Union[Unset, UserSummary] = UNSET
            _creator = d.pop("creator")
            if not isinstance(_creator, Unset):
                creator = UserSummary.from_dict(_creator)

            return creator

        creator = get_creator() if "creator" in d else cast(Union[Unset, UserSummary], UNSET)

        def get_custom_fields() -> Union[Unset, CustomFields]:
            custom_fields: Union[Unset, CustomFields] = UNSET
            _custom_fields = d.pop("customFields")
            if not isinstance(_custom_fields, Unset):
                custom_fields = CustomFields.from_dict(_custom_fields)

            return custom_fields

        custom_fields = (
            get_custom_fields() if "customFields" in d else cast(Union[Unset, CustomFields], UNSET)
        )

        def get_entity_registry_id() -> Union[Unset, None, str]:
            entity_registry_id = d.pop("entityRegistryId")
            return entity_registry_id

        entity_registry_id = (
            get_entity_registry_id() if "entityRegistryId" in d else cast(Union[Unset, None, str], UNSET)
        )

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_folder_id() -> Union[Unset, None, str]:
            folder_id = d.pop("folderId")
            return folder_id

        folder_id = get_folder_id() if "folderId" in d else cast(Union[Unset, None, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_length() -> Union[Unset, int]:
            length = d.pop("length")
            return length

        length = get_length() if "length" in d else cast(Union[Unset, int], UNSET)

        def get_modified_at() -> Union[Unset, datetime.datetime]:
            modified_at: Union[Unset, datetime.datetime] = UNSET
            _modified_at = d.pop("modifiedAt")
            if _modified_at is not None and not isinstance(_modified_at, Unset):
                modified_at = isoparse(cast(str, _modified_at))

            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_nucleotide_type() -> Union[Unset, OligoNucleotideType]:
            nucleotide_type = None
            _nucleotide_type = d.pop("nucleotideType")
            if _nucleotide_type is not None and _nucleotide_type is not UNSET:
                try:
                    nucleotide_type = OligoNucleotideType(_nucleotide_type)
                except ValueError:
                    nucleotide_type = OligoNucleotideType.of_unknown(_nucleotide_type)

            return nucleotide_type

        nucleotide_type = (
            get_nucleotide_type() if "nucleotideType" in d else cast(Union[Unset, OligoNucleotideType], UNSET)
        )

        def get_registration_origin() -> Union[Unset, None, RegistrationOrigin]:
            registration_origin = None
            _registration_origin = d.pop("registrationOrigin")
            if _registration_origin is not None and not isinstance(_registration_origin, Unset):
                registration_origin = RegistrationOrigin.from_dict(_registration_origin)

            return registration_origin

        registration_origin = (
            get_registration_origin()
            if "registrationOrigin" in d
            else cast(Union[Unset, None, RegistrationOrigin], UNSET)
        )

        def get_registry_id() -> Union[Unset, None, str]:
            registry_id = d.pop("registryId")
            return registry_id

        registry_id = get_registry_id() if "registryId" in d else cast(Union[Unset, None, str], UNSET)

        def get_schema() -> Union[Unset, None, SchemaSummary]:
            schema = None
            _schema = d.pop("schema")
            if _schema is not None and not isinstance(_schema, Unset):
                schema = SchemaSummary.from_dict(_schema)

            return schema

        schema = get_schema() if "schema" in d else cast(Union[Unset, None, SchemaSummary], UNSET)

        def get_web_url() -> Union[Unset, str]:
            web_url = d.pop("webURL")
            return web_url

        web_url = get_web_url() if "webURL" in d else cast(Union[Unset, str], UNSET)

        dna_oligo_helm = cls(
            helm=helm,
            api_url=api_url,
            bases=bases,
            aliases=aliases,
            archive_record=archive_record,
            created_at=created_at,
            creator=creator,
            custom_fields=custom_fields,
            entity_registry_id=entity_registry_id,
            fields=fields,
            folder_id=folder_id,
            id=id,
            length=length,
            modified_at=modified_at,
            name=name,
            nucleotide_type=nucleotide_type,
            registration_origin=registration_origin,
            registry_id=registry_id,
            schema=schema,
            web_url=web_url,
        )

        dna_oligo_helm.additional_properties = d
        return dna_oligo_helm

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
    def helm(self) -> str:
        """ Representation of the oligo in HELM syntax, including any chemical modifications """
        if isinstance(self._helm, Unset):
            raise NotPresentError(self, "helm")
        return self._helm

    @helm.setter
    def helm(self, value: str) -> None:
        self._helm = value

    @helm.deleter
    def helm(self) -> None:
        self._helm = UNSET

    @property
    def api_url(self) -> str:
        """ The canonical url of the Oligo in the API. """
        if isinstance(self._api_url, Unset):
            raise NotPresentError(self, "api_url")
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        self._api_url = UNSET

    @property
    def bases(self) -> str:
        """ Base pairs of the Oligo. """
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
    def aliases(self) -> List[str]:
        """ Array of aliases """
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
    def archive_record(self) -> Optional[ArchiveRecord]:
        if isinstance(self._archive_record, Unset):
            raise NotPresentError(self, "archive_record")
        return self._archive_record

    @archive_record.setter
    def archive_record(self, value: Optional[ArchiveRecord]) -> None:
        self._archive_record = value

    @archive_record.deleter
    def archive_record(self) -> None:
        self._archive_record = UNSET

    @property
    def created_at(self) -> datetime.datetime:
        """ DateTime the Oligo was created. """
        if isinstance(self._created_at, Unset):
            raise NotPresentError(self, "created_at")
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        self._created_at = value

    @created_at.deleter
    def created_at(self) -> None:
        self._created_at = UNSET

    @property
    def creator(self) -> UserSummary:
        if isinstance(self._creator, Unset):
            raise NotPresentError(self, "creator")
        return self._creator

    @creator.setter
    def creator(self, value: UserSummary) -> None:
        self._creator = value

    @creator.deleter
    def creator(self) -> None:
        self._creator = UNSET

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
    def entity_registry_id(self) -> Optional[str]:
        """ Registry ID of the Oligo if registered. """
        if isinstance(self._entity_registry_id, Unset):
            raise NotPresentError(self, "entity_registry_id")
        return self._entity_registry_id

    @entity_registry_id.setter
    def entity_registry_id(self, value: Optional[str]) -> None:
        self._entity_registry_id = value

    @entity_registry_id.deleter
    def entity_registry_id(self) -> None:
        self._entity_registry_id = UNSET

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
    def folder_id(self) -> Optional[str]:
        """ ID of the folder that contains the Oligo. """
        if isinstance(self._folder_id, Unset):
            raise NotPresentError(self, "folder_id")
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: Optional[str]) -> None:
        self._folder_id = value

    @folder_id.deleter
    def folder_id(self) -> None:
        self._folder_id = UNSET

    @property
    def id(self) -> str:
        """ ID of the Oligo. """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def length(self) -> int:
        """ Number of bases in the Oligo. """
        if isinstance(self._length, Unset):
            raise NotPresentError(self, "length")
        return self._length

    @length.setter
    def length(self, value: int) -> None:
        self._length = value

    @length.deleter
    def length(self) -> None:
        self._length = UNSET

    @property
    def modified_at(self) -> datetime.datetime:
        """ DateTime the Oligo was last modified. """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: datetime.datetime) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

    @property
    def name(self) -> str:
        """ Name of the Oligo. """
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
    def nucleotide_type(self) -> OligoNucleotideType:
        """ Nucleotide type of the Oligo. """
        if isinstance(self._nucleotide_type, Unset):
            raise NotPresentError(self, "nucleotide_type")
        return self._nucleotide_type

    @nucleotide_type.setter
    def nucleotide_type(self, value: OligoNucleotideType) -> None:
        self._nucleotide_type = value

    @nucleotide_type.deleter
    def nucleotide_type(self) -> None:
        self._nucleotide_type = UNSET

    @property
    def registration_origin(self) -> Optional[RegistrationOrigin]:
        if isinstance(self._registration_origin, Unset):
            raise NotPresentError(self, "registration_origin")
        return self._registration_origin

    @registration_origin.setter
    def registration_origin(self, value: Optional[RegistrationOrigin]) -> None:
        self._registration_origin = value

    @registration_origin.deleter
    def registration_origin(self) -> None:
        self._registration_origin = UNSET

    @property
    def registry_id(self) -> Optional[str]:
        """ Registry the Oligo is registered in. """
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: Optional[str]) -> None:
        self._registry_id = value

    @registry_id.deleter
    def registry_id(self) -> None:
        self._registry_id = UNSET

    @property
    def schema(self) -> Optional[SchemaSummary]:
        if isinstance(self._schema, Unset):
            raise NotPresentError(self, "schema")
        return self._schema

    @schema.setter
    def schema(self, value: Optional[SchemaSummary]) -> None:
        self._schema = value

    @schema.deleter
    def schema(self) -> None:
        self._schema = UNSET

    @property
    def web_url(self) -> str:
        """ URL of the Oligo. """
        if isinstance(self._web_url, Unset):
            raise NotPresentError(self, "web_url")
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @web_url.deleter
    def web_url(self) -> None:
        self._web_url = UNSET
