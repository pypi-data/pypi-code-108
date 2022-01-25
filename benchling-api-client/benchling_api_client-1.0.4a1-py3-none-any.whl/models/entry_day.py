from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.assay_run_note_part import AssayRunNotePart
from ..models.box_creation_table_note_part import BoxCreationTableNotePart
from ..models.checkbox_note_part import CheckboxNotePart
from ..models.external_file_note_part import ExternalFileNotePart
from ..models.mixture_prep_table_note_part import MixturePrepTableNotePart
from ..models.plate_creation_table_note_part import PlateCreationTableNotePart
from ..models.registration_table_note_part import RegistrationTableNotePart
from ..models.results_table_note_part import ResultsTableNotePart
from ..models.simple_note_part import SimpleNotePart
from ..models.table_note_part import TableNotePart
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryDay")


@attr.s(auto_attribs=True, repr=False)
class EntryDay:
    """  """

    _date: Union[Unset, str] = UNSET
    _notes: Union[
        Unset,
        List[
            Union[
                SimpleNotePart,
                TableNotePart,
                CheckboxNotePart,
                ExternalFileNotePart,
                AssayRunNotePart,
                ResultsTableNotePart,
                RegistrationTableNotePart,
                PlateCreationTableNotePart,
                BoxCreationTableNotePart,
                MixturePrepTableNotePart,
                UnknownType,
            ]
        ],
    ] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("date={}".format(repr(self._date)))
        fields.append("notes={}".format(repr(self._notes)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntryDay({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        date = self._date
        notes: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._notes, Unset):
            notes = []
            for notes_item_data in self._notes:
                if isinstance(notes_item_data, UnknownType):
                    notes_item = notes_item_data.value
                elif isinstance(notes_item_data, SimpleNotePart):
                    notes_item = notes_item_data.to_dict()

                elif isinstance(notes_item_data, TableNotePart):
                    notes_item = notes_item_data.to_dict()

                elif isinstance(notes_item_data, CheckboxNotePart):
                    notes_item = notes_item_data.to_dict()

                elif isinstance(notes_item_data, ExternalFileNotePart):
                    notes_item = notes_item_data.to_dict()

                elif isinstance(notes_item_data, AssayRunNotePart):
                    notes_item = notes_item_data.to_dict()

                elif isinstance(notes_item_data, ResultsTableNotePart):
                    notes_item = notes_item_data.to_dict()

                elif isinstance(notes_item_data, RegistrationTableNotePart):
                    notes_item = notes_item_data.to_dict()

                elif isinstance(notes_item_data, PlateCreationTableNotePart):
                    notes_item = notes_item_data.to_dict()

                elif isinstance(notes_item_data, BoxCreationTableNotePart):
                    notes_item = notes_item_data.to_dict()

                else:
                    notes_item = notes_item_data.to_dict()

                notes.append(notes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if date is not UNSET:
            field_dict["date"] = date
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_date() -> Union[Unset, str]:
            date = d.pop("date")
            return date

        date = get_date() if "date" in d else cast(Union[Unset, str], UNSET)

        def get_notes() -> Union[
            Unset,
            List[
                Union[
                    SimpleNotePart,
                    TableNotePart,
                    CheckboxNotePart,
                    ExternalFileNotePart,
                    AssayRunNotePart,
                    ResultsTableNotePart,
                    RegistrationTableNotePart,
                    PlateCreationTableNotePart,
                    BoxCreationTableNotePart,
                    MixturePrepTableNotePart,
                    UnknownType,
                ]
            ],
        ]:
            notes = []
            _notes = d.pop("notes")
            for notes_item_data in _notes or []:

                def _parse_notes_item(
                    data: Union[Dict[str, Any]]
                ) -> Union[
                    SimpleNotePart,
                    TableNotePart,
                    CheckboxNotePart,
                    ExternalFileNotePart,
                    AssayRunNotePart,
                    ResultsTableNotePart,
                    RegistrationTableNotePart,
                    PlateCreationTableNotePart,
                    BoxCreationTableNotePart,
                    MixturePrepTableNotePart,
                    UnknownType,
                ]:
                    notes_item: Union[
                        SimpleNotePart,
                        TableNotePart,
                        CheckboxNotePart,
                        ExternalFileNotePart,
                        AssayRunNotePart,
                        ResultsTableNotePart,
                        RegistrationTableNotePart,
                        PlateCreationTableNotePart,
                        BoxCreationTableNotePart,
                        MixturePrepTableNotePart,
                        UnknownType,
                    ]
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        notes_item = SimpleNotePart.from_dict(data)

                        return notes_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        notes_item = TableNotePart.from_dict(data)

                        return notes_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        notes_item = CheckboxNotePart.from_dict(data)

                        return notes_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        notes_item = ExternalFileNotePart.from_dict(data)

                        return notes_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        notes_item = AssayRunNotePart.from_dict(data)

                        return notes_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        notes_item = ResultsTableNotePart.from_dict(data)

                        return notes_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        notes_item = RegistrationTableNotePart.from_dict(data)

                        return notes_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        notes_item = PlateCreationTableNotePart.from_dict(data)

                        return notes_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        notes_item = BoxCreationTableNotePart.from_dict(data)

                        return notes_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        notes_item = MixturePrepTableNotePart.from_dict(data)

                        return notes_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                notes_item = _parse_notes_item(notes_item_data)

                notes.append(notes_item)

            return notes

        notes = (
            get_notes()
            if "notes" in d
            else cast(
                Union[
                    Unset,
                    List[
                        Union[
                            SimpleNotePart,
                            TableNotePart,
                            CheckboxNotePart,
                            ExternalFileNotePart,
                            AssayRunNotePart,
                            ResultsTableNotePart,
                            RegistrationTableNotePart,
                            PlateCreationTableNotePart,
                            BoxCreationTableNotePart,
                            MixturePrepTableNotePart,
                            UnknownType,
                        ]
                    ],
                ],
                UNSET,
            )
        )

        entry_day = cls(
            date=date,
            notes=notes,
        )

        entry_day.additional_properties = d
        return entry_day

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
    def date(self) -> str:
        """ A Date string """
        if isinstance(self._date, Unset):
            raise NotPresentError(self, "date")
        return self._date

    @date.setter
    def date(self, value: str) -> None:
        self._date = value

    @date.deleter
    def date(self) -> None:
        self._date = UNSET

    @property
    def notes(
        self,
    ) -> List[
        Union[
            SimpleNotePart,
            TableNotePart,
            CheckboxNotePart,
            ExternalFileNotePart,
            AssayRunNotePart,
            ResultsTableNotePart,
            RegistrationTableNotePart,
            PlateCreationTableNotePart,
            BoxCreationTableNotePart,
            MixturePrepTableNotePart,
            UnknownType,
        ]
    ]:
        if isinstance(self._notes, Unset):
            raise NotPresentError(self, "notes")
        return self._notes

    @notes.setter
    def notes(
        self,
        value: List[
            Union[
                SimpleNotePart,
                TableNotePart,
                CheckboxNotePart,
                ExternalFileNotePart,
                AssayRunNotePart,
                ResultsTableNotePart,
                RegistrationTableNotePart,
                PlateCreationTableNotePart,
                BoxCreationTableNotePart,
                MixturePrepTableNotePart,
                UnknownType,
            ]
        ],
    ) -> None:
        self._notes = value

    @notes.deleter
    def notes(self) -> None:
        self._notes = UNSET
