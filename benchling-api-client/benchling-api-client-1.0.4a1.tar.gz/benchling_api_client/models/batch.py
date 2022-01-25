import datetime
from typing import Any, cast, Dict, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError, UnknownType
from ..models.aa_sequence_summary import AaSequenceSummary
from ..models.archive_record import ArchiveRecord
from ..models.custom_entity_summary import CustomEntitySummary
from ..models.dna_sequence_summary import DnaSequenceSummary
from ..models.fields import Fields
from ..models.measurement import Measurement
from ..models.schema_summary import SchemaSummary
from ..models.user_summary import UserSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="Batch")


@attr.s(auto_attribs=True, repr=False)
class Batch:
    """  """

    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    _created_at: Union[Unset, datetime.datetime] = UNSET
    _creator: Union[Unset, UserSummary] = UNSET
    _default_concentration: Union[Unset, Measurement] = UNSET
    _entity: Union[Unset, DnaSequenceSummary, AaSequenceSummary, CustomEntitySummary, UnknownType] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _name: Union[Unset, str] = UNSET
    _schema: Union[Unset, None, SchemaSummary] = UNSET
    _web_url: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("default_concentration={}".format(repr(self._default_concentration)))
        fields.append("entity={}".format(repr(self._entity)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("web_url={}".format(repr(self._web_url)))
        return "Batch({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        default_concentration: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._default_concentration, Unset):
            default_concentration = self._default_concentration.to_dict()

        entity: Union[Unset, Dict[str, Any]]
        if isinstance(self._entity, Unset):
            entity = UNSET
        elif isinstance(self._entity, UnknownType):
            entity = self._entity.value
        elif isinstance(self._entity, DnaSequenceSummary):
            entity = UNSET
            if not isinstance(self._entity, Unset):
                entity = self._entity.to_dict()

        elif isinstance(self._entity, AaSequenceSummary):
            entity = UNSET
            if not isinstance(self._entity, Unset):
                entity = self._entity.to_dict()

        else:
            entity = UNSET
            if not isinstance(self._entity, Unset):
                entity = self._entity.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        id = self._id
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        name = self._name
        schema: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._schema, Unset):
            schema = self._schema.to_dict() if self._schema else None

        web_url = self._web_url

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if creator is not UNSET:
            field_dict["creator"] = creator
        if default_concentration is not UNSET:
            field_dict["defaultConcentration"] = default_concentration
        if entity is not UNSET:
            field_dict["entity"] = entity
        if fields is not UNSET:
            field_dict["fields"] = fields
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if name is not UNSET:
            field_dict["name"] = name
        if schema is not UNSET:
            field_dict["schema"] = schema
        if web_url is not UNSET:
            field_dict["webURL"] = web_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

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

        def get_default_concentration() -> Union[Unset, Measurement]:
            default_concentration: Union[Unset, Measurement] = UNSET
            _default_concentration = d.pop("defaultConcentration")
            if not isinstance(_default_concentration, Unset):
                default_concentration = Measurement.from_dict(_default_concentration)

            return default_concentration

        default_concentration = (
            get_default_concentration()
            if "defaultConcentration" in d
            else cast(Union[Unset, Measurement], UNSET)
        )

        def get_entity() -> Union[
            Unset, DnaSequenceSummary, AaSequenceSummary, CustomEntitySummary, UnknownType
        ]:
            def _parse_entity(
                data: Union[Unset, Dict[str, Any]]
            ) -> Union[Unset, DnaSequenceSummary, AaSequenceSummary, CustomEntitySummary, UnknownType]:
                entity: Union[Unset, DnaSequenceSummary, AaSequenceSummary, CustomEntitySummary, UnknownType]
                if isinstance(data, Unset):
                    return data
                discriminator_value: str = cast(str, data.get("entityType"))
                if discriminator_value is not None:
                    if discriminator_value == "dna_sequence":
                        entity = UNSET
                        _entity = data
                        if not isinstance(_entity, Unset):
                            entity = DnaSequenceSummary.from_dict(_entity)

                        return entity
                    if discriminator_value == "aa_sequence":
                        entity = UNSET
                        _entity = data
                        if not isinstance(_entity, Unset):
                            entity = AaSequenceSummary.from_dict(_entity)

                        return entity
                    if discriminator_value == "custom_entity":
                        entity = UNSET
                        _entity = data
                        if not isinstance(_entity, Unset):
                            entity = CustomEntitySummary.from_dict(_entity)

                        return entity

                    return UnknownType(value=data)
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    entity = UNSET
                    _entity = data
                    if not isinstance(_entity, Unset):
                        entity = DnaSequenceSummary.from_dict(_entity)

                    return entity
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    entity = UNSET
                    _entity = data
                    if not isinstance(_entity, Unset):
                        entity = AaSequenceSummary.from_dict(_entity)

                    return entity
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    entity = UNSET
                    _entity = data
                    if not isinstance(_entity, Unset):
                        entity = CustomEntitySummary.from_dict(_entity)

                    return entity
                except:  # noqa: E722
                    pass
                return UnknownType(data)

            entity = _parse_entity(d.pop("entity"))

            return entity

        entity = (
            get_entity()
            if "entity" in d
            else cast(
                Union[Unset, DnaSequenceSummary, AaSequenceSummary, CustomEntitySummary, UnknownType], UNSET
            )
        )

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

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

        batch = cls(
            archive_record=archive_record,
            created_at=created_at,
            creator=creator,
            default_concentration=default_concentration,
            entity=entity,
            fields=fields,
            id=id,
            modified_at=modified_at,
            name=name,
            schema=schema,
            web_url=web_url,
        )

        return batch

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
        """ DateTime at which the the result was created """
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
    def default_concentration(self) -> Measurement:
        if isinstance(self._default_concentration, Unset):
            raise NotPresentError(self, "default_concentration")
        return self._default_concentration

    @default_concentration.setter
    def default_concentration(self, value: Measurement) -> None:
        self._default_concentration = value

    @default_concentration.deleter
    def default_concentration(self) -> None:
        self._default_concentration = UNSET

    @property
    def entity(self) -> Union[DnaSequenceSummary, AaSequenceSummary, CustomEntitySummary, UnknownType]:
        if isinstance(self._entity, Unset):
            raise NotPresentError(self, "entity")
        return self._entity

    @entity.setter
    def entity(
        self, value: Union[DnaSequenceSummary, AaSequenceSummary, CustomEntitySummary, UnknownType]
    ) -> None:
        self._entity = value

    @entity.deleter
    def entity(self) -> None:
        self._entity = UNSET

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
    def id(self) -> str:
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
    def modified_at(self) -> datetime.datetime:
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
        if isinstance(self._web_url, Unset):
            raise NotPresentError(self, "web_url")
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @web_url.deleter
    def web_url(self) -> None:
        self._web_url = UNSET
