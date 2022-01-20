from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_labels import ContainerLabels
from ..models.entity_labels import EntityLabels
from ..models.ingredient_amount import IngredientAmount
from ..models.ingredient_component_entity import IngredientComponentEntity
from ..models.ingredient_measurement_units import IngredientMeasurementUnits
from ..types import UNSET, Unset

T = TypeVar("T", bound="Ingredient")


@attr.s(auto_attribs=True, repr=False)
class Ingredient:
    """  """

    _amount: Union[Unset, IngredientAmount] = UNSET
    _catalog_identifier: Union[Unset, None, str] = UNSET
    _component_entity: Union[Unset, IngredientComponentEntity] = UNSET
    _component_lot_container: Union[Unset, None, ContainerLabels] = UNSET
    _component_lot_entity: Union[Unset, None, EntityLabels] = UNSET
    _component_lot_text: Union[Unset, None, str] = UNSET
    _has_parent: Union[Unset, bool] = UNSET
    _notes: Union[Unset, None, str] = UNSET
    _target_amount: Union[Unset, None, str] = UNSET
    _units: Union[Unset, IngredientMeasurementUnits] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("amount={}".format(repr(self._amount)))
        fields.append("catalog_identifier={}".format(repr(self._catalog_identifier)))
        fields.append("component_entity={}".format(repr(self._component_entity)))
        fields.append("component_lot_container={}".format(repr(self._component_lot_container)))
        fields.append("component_lot_entity={}".format(repr(self._component_lot_entity)))
        fields.append("component_lot_text={}".format(repr(self._component_lot_text)))
        fields.append("has_parent={}".format(repr(self._has_parent)))
        fields.append("notes={}".format(repr(self._notes)))
        fields.append("target_amount={}".format(repr(self._target_amount)))
        fields.append("units={}".format(repr(self._units)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Ingredient({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        amount: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._amount, Unset):
            amount = self._amount.to_dict()

        catalog_identifier = self._catalog_identifier
        component_entity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._component_entity, Unset):
            component_entity = self._component_entity.to_dict()

        component_lot_container: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._component_lot_container, Unset):
            component_lot_container = (
                self._component_lot_container.to_dict() if self._component_lot_container else None
            )

        component_lot_entity: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._component_lot_entity, Unset):
            component_lot_entity = (
                self._component_lot_entity.to_dict() if self._component_lot_entity else None
            )

        component_lot_text = self._component_lot_text
        has_parent = self._has_parent
        notes = self._notes
        target_amount = self._target_amount
        units: Union[Unset, int] = UNSET
        if not isinstance(self._units, Unset):
            units = self._units.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if amount is not UNSET:
            field_dict["amount"] = amount
        if catalog_identifier is not UNSET:
            field_dict["catalogIdentifier"] = catalog_identifier
        if component_entity is not UNSET:
            field_dict["componentEntity"] = component_entity
        if component_lot_container is not UNSET:
            field_dict["componentLotContainer"] = component_lot_container
        if component_lot_entity is not UNSET:
            field_dict["componentLotEntity"] = component_lot_entity
        if component_lot_text is not UNSET:
            field_dict["componentLotText"] = component_lot_text
        if has_parent is not UNSET:
            field_dict["hasParent"] = has_parent
        if notes is not UNSET:
            field_dict["notes"] = notes
        if target_amount is not UNSET:
            field_dict["targetAmount"] = target_amount
        if units is not UNSET:
            field_dict["units"] = units

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_amount() -> Union[Unset, IngredientAmount]:
            amount: Union[Unset, IngredientAmount] = UNSET
            _amount = d.pop("amount")
            if not isinstance(_amount, Unset):
                amount = IngredientAmount.from_dict(_amount)

            return amount

        amount = get_amount() if "amount" in d else cast(Union[Unset, IngredientAmount], UNSET)

        def get_catalog_identifier() -> Union[Unset, None, str]:
            catalog_identifier = d.pop("catalogIdentifier")
            return catalog_identifier

        catalog_identifier = (
            get_catalog_identifier() if "catalogIdentifier" in d else cast(Union[Unset, None, str], UNSET)
        )

        def get_component_entity() -> Union[Unset, IngredientComponentEntity]:
            component_entity: Union[Unset, IngredientComponentEntity] = UNSET
            _component_entity = d.pop("componentEntity")
            if not isinstance(_component_entity, Unset):
                component_entity = IngredientComponentEntity.from_dict(_component_entity)

            return component_entity

        component_entity = (
            get_component_entity()
            if "componentEntity" in d
            else cast(Union[Unset, IngredientComponentEntity], UNSET)
        )

        def get_component_lot_container() -> Union[Unset, None, ContainerLabels]:
            component_lot_container = None
            _component_lot_container = d.pop("componentLotContainer")
            if _component_lot_container is not None and not isinstance(_component_lot_container, Unset):
                component_lot_container = ContainerLabels.from_dict(_component_lot_container)

            return component_lot_container

        component_lot_container = (
            get_component_lot_container()
            if "componentLotContainer" in d
            else cast(Union[Unset, None, ContainerLabels], UNSET)
        )

        def get_component_lot_entity() -> Union[Unset, None, EntityLabels]:
            component_lot_entity = None
            _component_lot_entity = d.pop("componentLotEntity")
            if _component_lot_entity is not None and not isinstance(_component_lot_entity, Unset):
                component_lot_entity = EntityLabels.from_dict(_component_lot_entity)

            return component_lot_entity

        component_lot_entity = (
            get_component_lot_entity()
            if "componentLotEntity" in d
            else cast(Union[Unset, None, EntityLabels], UNSET)
        )

        def get_component_lot_text() -> Union[Unset, None, str]:
            component_lot_text = d.pop("componentLotText")
            return component_lot_text

        component_lot_text = (
            get_component_lot_text() if "componentLotText" in d else cast(Union[Unset, None, str], UNSET)
        )

        def get_has_parent() -> Union[Unset, bool]:
            has_parent = d.pop("hasParent")
            return has_parent

        has_parent = get_has_parent() if "hasParent" in d else cast(Union[Unset, bool], UNSET)

        def get_notes() -> Union[Unset, None, str]:
            notes = d.pop("notes")
            return notes

        notes = get_notes() if "notes" in d else cast(Union[Unset, None, str], UNSET)

        def get_target_amount() -> Union[Unset, None, str]:
            target_amount = d.pop("targetAmount")
            return target_amount

        target_amount = get_target_amount() if "targetAmount" in d else cast(Union[Unset, None, str], UNSET)

        def get_units() -> Union[Unset, IngredientMeasurementUnits]:
            units = None
            _units = d.pop("units")
            if _units is not None and _units is not UNSET:
                try:
                    units = IngredientMeasurementUnits(_units)
                except ValueError:
                    units = IngredientMeasurementUnits.of_unknown(_units)

            return units

        units = get_units() if "units" in d else cast(Union[Unset, IngredientMeasurementUnits], UNSET)

        ingredient = cls(
            amount=amount,
            catalog_identifier=catalog_identifier,
            component_entity=component_entity,
            component_lot_container=component_lot_container,
            component_lot_entity=component_lot_entity,
            component_lot_text=component_lot_text,
            has_parent=has_parent,
            notes=notes,
            target_amount=target_amount,
            units=units,
        )

        ingredient.additional_properties = d
        return ingredient

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

    @amount.deleter
    def amount(self) -> None:
        self._amount = UNSET

    @property
    def catalog_identifier(self) -> Optional[str]:
        if isinstance(self._catalog_identifier, Unset):
            raise NotPresentError(self, "catalog_identifier")
        return self._catalog_identifier

    @catalog_identifier.setter
    def catalog_identifier(self, value: Optional[str]) -> None:
        self._catalog_identifier = value

    @catalog_identifier.deleter
    def catalog_identifier(self) -> None:
        self._catalog_identifier = UNSET

    @property
    def component_entity(self) -> IngredientComponentEntity:
        if isinstance(self._component_entity, Unset):
            raise NotPresentError(self, "component_entity")
        return self._component_entity

    @component_entity.setter
    def component_entity(self, value: IngredientComponentEntity) -> None:
        self._component_entity = value

    @component_entity.deleter
    def component_entity(self) -> None:
        self._component_entity = UNSET

    @property
    def component_lot_container(self) -> Optional[ContainerLabels]:
        if isinstance(self._component_lot_container, Unset):
            raise NotPresentError(self, "component_lot_container")
        return self._component_lot_container

    @component_lot_container.setter
    def component_lot_container(self, value: Optional[ContainerLabels]) -> None:
        self._component_lot_container = value

    @component_lot_container.deleter
    def component_lot_container(self) -> None:
        self._component_lot_container = UNSET

    @property
    def component_lot_entity(self) -> Optional[EntityLabels]:
        if isinstance(self._component_lot_entity, Unset):
            raise NotPresentError(self, "component_lot_entity")
        return self._component_lot_entity

    @component_lot_entity.setter
    def component_lot_entity(self, value: Optional[EntityLabels]) -> None:
        self._component_lot_entity = value

    @component_lot_entity.deleter
    def component_lot_entity(self) -> None:
        self._component_lot_entity = UNSET

    @property
    def component_lot_text(self) -> Optional[str]:
        """ Text representing the component lot for this ingredient. This is only present if the mixture schema supports component lots in "text" format. """
        if isinstance(self._component_lot_text, Unset):
            raise NotPresentError(self, "component_lot_text")
        return self._component_lot_text

    @component_lot_text.setter
    def component_lot_text(self, value: Optional[str]) -> None:
        self._component_lot_text = value

    @component_lot_text.deleter
    def component_lot_text(self) -> None:
        self._component_lot_text = UNSET

    @property
    def has_parent(self) -> bool:
        if isinstance(self._has_parent, Unset):
            raise NotPresentError(self, "has_parent")
        return self._has_parent

    @has_parent.setter
    def has_parent(self, value: bool) -> None:
        self._has_parent = value

    @has_parent.deleter
    def has_parent(self) -> None:
        self._has_parent = UNSET

    @property
    def notes(self) -> Optional[str]:
        if isinstance(self._notes, Unset):
            raise NotPresentError(self, "notes")
        return self._notes

    @notes.setter
    def notes(self, value: Optional[str]) -> None:
        self._notes = value

    @notes.deleter
    def notes(self) -> None:
        self._notes = UNSET

    @property
    def target_amount(self) -> Optional[str]:
        """ The target amount for this ingredient such that this ingredient's proportion in its mixture would preserve the equivalent ingredient's proportion in the parent mixture. Pair with `units`. """
        if isinstance(self._target_amount, Unset):
            raise NotPresentError(self, "target_amount")
        return self._target_amount

    @target_amount.setter
    def target_amount(self, value: Optional[str]) -> None:
        self._target_amount = value

    @target_amount.deleter
    def target_amount(self) -> None:
        self._target_amount = UNSET

    @property
    def units(self) -> IngredientMeasurementUnits:
        if isinstance(self._units, Unset):
            raise NotPresentError(self, "units")
        return self._units

    @units.setter
    def units(self, value: IngredientMeasurementUnits) -> None:
        self._units = value

    @units.deleter
    def units(self) -> None:
        self._units = UNSET
