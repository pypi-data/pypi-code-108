from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.ingredient_amount import IngredientAmount
from ..models.ingredient_measurement_units import IngredientMeasurementUnits
from ..types import UNSET, Unset

T = TypeVar("T", bound="IngredientWriteParams")


@attr.s(auto_attribs=True, repr=False)
class IngredientWriteParams:
    """  """

    _amount: IngredientAmount
    _component_entity_id: str
    _units: IngredientMeasurementUnits
    _catalog_identifier: Optional[str]
    _component_lot_container_id: Optional[str]
    _component_lot_entity_id: Optional[str]
    _component_lot_text: Optional[str]
    _notes: Optional[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("amount={}".format(repr(self._amount)))
        fields.append("component_entity_id={}".format(repr(self._component_entity_id)))
        fields.append("units={}".format(repr(self._units)))
        fields.append("catalog_identifier={}".format(repr(self._catalog_identifier)))
        fields.append("component_lot_container_id={}".format(repr(self._component_lot_container_id)))
        fields.append("component_lot_entity_id={}".format(repr(self._component_lot_entity_id)))
        fields.append("component_lot_text={}".format(repr(self._component_lot_text)))
        fields.append("notes={}".format(repr(self._notes)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "IngredientWriteParams({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        amount = self._amount.to_dict()

        component_entity_id = self._component_entity_id
        units = self._units.value

        catalog_identifier = self._catalog_identifier
        component_lot_container_id = self._component_lot_container_id
        component_lot_entity_id = self._component_lot_entity_id
        component_lot_text = self._component_lot_text
        notes = self._notes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
                "componentEntityId": component_entity_id,
                "units": units,
                "catalogIdentifier": catalog_identifier,
                "componentLotContainerId": component_lot_container_id,
                "componentLotEntityId": component_lot_entity_id,
                "componentLotText": component_lot_text,
                "notes": notes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_amount() -> IngredientAmount:
            amount = IngredientAmount.from_dict(d.pop("amount"))

            return amount

        amount = get_amount() if "amount" in d else cast(IngredientAmount, UNSET)

        def get_component_entity_id() -> str:
            component_entity_id = d.pop("componentEntityId")
            return component_entity_id

        component_entity_id = get_component_entity_id() if "componentEntityId" in d else cast(str, UNSET)

        def get_units() -> IngredientMeasurementUnits:
            _units = d.pop("units")
            try:
                units = IngredientMeasurementUnits(_units)
            except ValueError:
                units = IngredientMeasurementUnits.of_unknown(_units)

            return units

        units = get_units() if "units" in d else cast(IngredientMeasurementUnits, UNSET)

        def get_catalog_identifier() -> Optional[str]:
            catalog_identifier = d.pop("catalogIdentifier")
            return catalog_identifier

        catalog_identifier = (
            get_catalog_identifier() if "catalogIdentifier" in d else cast(Optional[str], UNSET)
        )

        def get_component_lot_container_id() -> Optional[str]:
            component_lot_container_id = d.pop("componentLotContainerId")
            return component_lot_container_id

        component_lot_container_id = (
            get_component_lot_container_id() if "componentLotContainerId" in d else cast(Optional[str], UNSET)
        )

        def get_component_lot_entity_id() -> Optional[str]:
            component_lot_entity_id = d.pop("componentLotEntityId")
            return component_lot_entity_id

        component_lot_entity_id = (
            get_component_lot_entity_id() if "componentLotEntityId" in d else cast(Optional[str], UNSET)
        )

        def get_component_lot_text() -> Optional[str]:
            component_lot_text = d.pop("componentLotText")
            return component_lot_text

        component_lot_text = (
            get_component_lot_text() if "componentLotText" in d else cast(Optional[str], UNSET)
        )

        def get_notes() -> Optional[str]:
            notes = d.pop("notes")
            return notes

        notes = get_notes() if "notes" in d else cast(Optional[str], UNSET)

        ingredient_write_params = cls(
            amount=amount,
            component_entity_id=component_entity_id,
            units=units,
            catalog_identifier=catalog_identifier,
            component_lot_container_id=component_lot_container_id,
            component_lot_entity_id=component_lot_entity_id,
            component_lot_text=component_lot_text,
            notes=notes,
        )

        ingredient_write_params.additional_properties = d
        return ingredient_write_params

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
    def amount(self) -> IngredientAmount:
        """The amount value of this ingredient in its mixture, in string format (to preserve full precision). Pair with `units`. Supports scientific notation (1.23e4). One ingredient on this mixture can have an amount value of `"QS"`."""
        if isinstance(self._amount, Unset):
            raise NotPresentError(self, "amount")
        return self._amount

    @amount.setter
    def amount(self, value: IngredientAmount) -> None:
        self._amount = value

    @property
    def component_entity_id(self) -> str:
        """ The entity that uniquely identifies this component. """
        if isinstance(self._component_entity_id, Unset):
            raise NotPresentError(self, "component_entity_id")
        return self._component_entity_id

    @component_entity_id.setter
    def component_entity_id(self, value: str) -> None:
        self._component_entity_id = value

    @property
    def units(self) -> IngredientMeasurementUnits:
        if isinstance(self._units, Unset):
            raise NotPresentError(self, "units")
        return self._units

    @units.setter
    def units(self, value: IngredientMeasurementUnits) -> None:
        self._units = value

    @property
    def catalog_identifier(self) -> Optional[str]:
        if isinstance(self._catalog_identifier, Unset):
            raise NotPresentError(self, "catalog_identifier")
        return self._catalog_identifier

    @catalog_identifier.setter
    def catalog_identifier(self, value: Optional[str]) -> None:
        self._catalog_identifier = value

    @property
    def component_lot_container_id(self) -> Optional[str]:
        """ The container representing the component lot for this ingredient. This is only writable if the mixture schema supports component lots in "storage" format. """
        if isinstance(self._component_lot_container_id, Unset):
            raise NotPresentError(self, "component_lot_container_id")
        return self._component_lot_container_id

    @component_lot_container_id.setter
    def component_lot_container_id(self, value: Optional[str]) -> None:
        self._component_lot_container_id = value

    @property
    def component_lot_entity_id(self) -> Optional[str]:
        """ The entity representing the component lot for this ingredient. This is only writable if the mixture schema supports component lots in "storage" format. """
        if isinstance(self._component_lot_entity_id, Unset):
            raise NotPresentError(self, "component_lot_entity_id")
        return self._component_lot_entity_id

    @component_lot_entity_id.setter
    def component_lot_entity_id(self, value: Optional[str]) -> None:
        self._component_lot_entity_id = value

    @property
    def component_lot_text(self) -> Optional[str]:
        """ Text representing the component lot for this ingredient. This is only writable if the mixture schema supports component lots in "text" format. """
        if isinstance(self._component_lot_text, Unset):
            raise NotPresentError(self, "component_lot_text")
        return self._component_lot_text

    @component_lot_text.setter
    def component_lot_text(self, value: Optional[str]) -> None:
        self._component_lot_text = value

    @property
    def notes(self) -> Optional[str]:
        if isinstance(self._notes, Unset):
            raise NotPresentError(self, "notes")
        return self._notes

    @notes.setter
    def notes(self, value: Optional[str]) -> None:
        self._notes = value
