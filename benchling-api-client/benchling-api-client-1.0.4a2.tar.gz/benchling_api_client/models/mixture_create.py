from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.custom_fields import CustomFields
from ..models.fields import Fields
from ..models.ingredient_write_params import IngredientWriteParams
from ..models.mixture_measurement_units import MixtureMeasurementUnits
from ..models.naming_strategy import NamingStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="MixtureCreate")


@attr.s(auto_attribs=True, repr=False)
class MixtureCreate:
    """  """

    _entity_registry_id: Union[Unset, str] = UNSET
    _folder_id: Union[Unset, str] = UNSET
    _naming_strategy: Union[Unset, NamingStrategy] = UNSET
    _registry_id: Union[Unset, str] = UNSET
    _aliases: Union[Unset, List[str]] = UNSET
    _amount: Union[Unset, str] = UNSET
    _author_ids: Union[Unset, List[str]] = UNSET
    _custom_fields: Union[Unset, CustomFields] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _ingredients: Union[Unset, List[IngredientWriteParams]] = UNSET
    _name: Union[Unset, str] = UNSET
    _schema_id: Union[Unset, str] = UNSET
    _units: Union[Unset, MixtureMeasurementUnits] = UNSET

    def __repr__(self):
        fields = []
        fields.append("entity_registry_id={}".format(repr(self._entity_registry_id)))
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("naming_strategy={}".format(repr(self._naming_strategy)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("aliases={}".format(repr(self._aliases)))
        fields.append("amount={}".format(repr(self._amount)))
        fields.append("author_ids={}".format(repr(self._author_ids)))
        fields.append("custom_fields={}".format(repr(self._custom_fields)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("ingredients={}".format(repr(self._ingredients)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("units={}".format(repr(self._units)))
        return "MixtureCreate({})".format(", ".join(fields))

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

        amount = self._amount
        author_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._author_ids, Unset):
            author_ids = self._author_ids

        custom_fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._custom_fields, Unset):
            custom_fields = self._custom_fields.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        ingredients: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._ingredients, Unset):
            ingredients = []
            for ingredients_item_data in self._ingredients:
                ingredients_item = ingredients_item_data.to_dict()

                ingredients.append(ingredients_item)

        name = self._name
        schema_id = self._schema_id
        units: Union[Unset, int] = UNSET
        if not isinstance(self._units, Unset):
            units = self._units.value

        field_dict: Dict[str, Any] = {}
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
        if amount is not UNSET:
            field_dict["amount"] = amount
        if author_ids is not UNSET:
            field_dict["authorIds"] = author_ids
        if custom_fields is not UNSET:
            field_dict["customFields"] = custom_fields
        if fields is not UNSET:
            field_dict["fields"] = fields
        if ingredients is not UNSET:
            field_dict["ingredients"] = ingredients
        if name is not UNSET:
            field_dict["name"] = name
        if schema_id is not UNSET:
            field_dict["schemaId"] = schema_id
        if units is not UNSET:
            field_dict["units"] = units

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

        def get_amount() -> Union[Unset, str]:
            amount = d.pop("amount")
            return amount

        amount = get_amount() if "amount" in d else cast(Union[Unset, str], UNSET)

        def get_author_ids() -> Union[Unset, List[str]]:
            author_ids = cast(List[str], d.pop("authorIds"))

            return author_ids

        author_ids = get_author_ids() if "authorIds" in d else cast(Union[Unset, List[str]], UNSET)

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

        def get_ingredients() -> Union[Unset, List[IngredientWriteParams]]:
            ingredients = []
            _ingredients = d.pop("ingredients")
            for ingredients_item_data in _ingredients or []:
                ingredients_item = IngredientWriteParams.from_dict(ingredients_item_data)

                ingredients.append(ingredients_item)

            return ingredients

        ingredients = (
            get_ingredients()
            if "ingredients" in d
            else cast(Union[Unset, List[IngredientWriteParams]], UNSET)
        )

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_schema_id() -> Union[Unset, str]:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(Union[Unset, str], UNSET)

        def get_units() -> Union[Unset, MixtureMeasurementUnits]:
            units = None
            _units = d.pop("units")
            if _units is not None and _units is not UNSET:
                try:
                    units = MixtureMeasurementUnits(_units)
                except ValueError:
                    units = MixtureMeasurementUnits.of_unknown(_units)

            return units

        units = get_units() if "units" in d else cast(Union[Unset, MixtureMeasurementUnits], UNSET)

        mixture_create = cls(
            entity_registry_id=entity_registry_id,
            folder_id=folder_id,
            naming_strategy=naming_strategy,
            registry_id=registry_id,
            aliases=aliases,
            amount=amount,
            author_ids=author_ids,
            custom_fields=custom_fields,
            fields=fields,
            ingredients=ingredients,
            name=name,
            schema_id=schema_id,
            units=units,
        )

        return mixture_create

    @property
    def entity_registry_id(self) -> str:
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
        """ ID of the folder that the entity is moved into """
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
        """ Aliases to add to the mixture """
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
    def amount(self) -> str:
        """ The positive numerical amount value of this mixture in string format (to preserve full precision). Pair with `units`. Supports scientific notation (1.23e4). """
        if isinstance(self._amount, Unset):
            raise NotPresentError(self, "amount")
        return self._amount

    @amount.setter
    def amount(self, value: str) -> None:
        self._amount = value

    @amount.deleter
    def amount(self) -> None:
        self._amount = UNSET

    @property
    def author_ids(self) -> List[str]:
        """ IDs of users to set as the mixture's authors. """
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
    def ingredients(self) -> List[IngredientWriteParams]:
        """Desired final state for the ingredients on this mixture.
        Each ingredient you specify will be matched with the existing ingredients on the mixture based on the component entity, and Benchling will create, update, or delete this mixture's ingredients so that the final state of this mixture's ingredients matches your request.
        Benchling will recognize that any ingredients you specify that match ingredients on the parent mixture (based on component entity) are inherited. This can be seen on the returned `ingredients[i].hasParent` attribute.
        """
        if isinstance(self._ingredients, Unset):
            raise NotPresentError(self, "ingredients")
        return self._ingredients

    @ingredients.setter
    def ingredients(self, value: List[IngredientWriteParams]) -> None:
        self._ingredients = value

    @ingredients.deleter
    def ingredients(self) -> None:
        self._ingredients = UNSET

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
    def schema_id(self) -> str:
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
    def units(self) -> MixtureMeasurementUnits:
        if isinstance(self._units, Unset):
            raise NotPresentError(self, "units")
        return self._units

    @units.setter
    def units(self, value: MixtureMeasurementUnits) -> None:
        self._units = value

    @units.deleter
    def units(self) -> None:
        self._units = UNSET
