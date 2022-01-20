from __future__ import annotations

__all__ = [
    "Model",
    "BaseModel",
]

import copy
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from types import TracebackType
from typing import Any, Dict, List, Optional

import libsbml

from .utils import convert_id_to_sbml, warning_on_one_line

warnings.formatwarning = warning_on_one_line  # type: ignore


@dataclass
class Model:
    """Meta-info container for model."""

    sbo: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    units: dict = field(default_factory=dict)
    compartments: dict = field(default_factory=dict)
    notes: dict = field(default_factory=dict)


class BaseModel(ABC):
    """Abstract model class."""

    def __init__(self, meta_info: Dict[str, Any] = None) -> None:
        default_meta_info: Dict[str, Any] = {
            "sbo": "SBO:0000004",  # modelling framework
            "id": f"modelbase-model-{datetime.now().date().strftime('%Y-%m-%d')}",
            "name": "modelbase-model",
            "units": {
                "per_second": {
                    "kind": libsbml.UNIT_KIND_SECOND,
                    "exponent": -1,
                    "scale": 0,
                    "multiplier": 1,
                },
            },
            "compartments": {
                "c": {
                    "name": "cytosol",
                    "is_constant": True,
                    "size": 1,
                    "spatial_dimensions": 3,
                    "units": "litre",
                }
            },
        }
        if meta_info is not None:
            default_meta_info.update(meta_info)
        self.meta_info: Dict[str, Any] = {"model": Model(**default_meta_info)}
        self._ids: set[str] = set()
        self._copy = None

    def __enter__(self) -> Any:
        """Enter the context manager.

        Returns
        -------
            Deepcopy of the model object
        """
        self._copy = self.copy()
        return self.copy()

    def __exit__(
        self,
        exception_type: Optional[BaseException],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> None:
        """Exit the context manager.

        Restores any changes made to the model structure.
        """
        self.__dict__ = self._copy.__dict__

    def copy(self) -> Any:
        """Create a deepcopy of the model.

        Returns
        -------
        model
            Deepcopy of the model object
        """
        return copy.deepcopy(self)

    def _check_for_existence(
        self,
        *,
        name: str,
        check_against: List[str],
        candidates: List[str],
        element_type: str,
        raise_on_missing: bool = False,
    ) -> None:
        to_check = set(check_against)
        to_check.add("time")
        for i in set(candidates).difference(to_check):
            if raise_on_missing:
                raise KeyError(f"Could not find {element_type} {i} for {name}")
            warnings.warn(f"Could not find {element_type} {i} for {name}")

    def _check_and_insert_ids(self, ids: List[str], context: str) -> None:
        for id_ in ids:
            if id_ in self._ids:
                warnings.warn(
                    f"{context}: Id {id_} already exists in the model. This might lead to variable shading!"
                )
            self._ids.add(id_)

    def _update_ids(self, ids: Dict[str, str]) -> None:
        for k, v in ids.items():
            self._ids.remove(k)
            self._ids.add(v)

    def _remove_ids(self, ids: List[str]) -> None:
        for id_ in ids:
            try:
                self._ids.remove(id_)
            except KeyError:
                warnings.warn("Could not find id. Do you have duplicate ids in the model?")

    def update_meta_info(self, component: str, meta_info: dict) -> None:
        """Add meta info for any given model component.

        Parameters
        ----------
        component : str
            Name of the component. Available components depend of the model type
        meta_info : dict
            Meta info for the component. Available keys depend on the
            component
        """
        for k1, d in meta_info.items():
            if isinstance(d, dict):
                for k2, v in d.items():
                    setattr(self.meta_info[component][k1], k2, v)
            else:
                setattr(self.meta_info[component], k1, d)

    def _get_nonzero_meta_info(self, *, component: str) -> Dict[str, Any]:
        """Get meta info of a component for all entries that are not None.

        Parameters
        ----------
        component : str
            Name of the component. Available components depend of the model type
        """
        meta_info = {}
        for k1, v1 in self.meta_info[component].items():
            info = {k2: v2 for k2, v2 in v1.__dict__.items() if bool(v2)}
            if bool(info):
                meta_info[k1] = info
        return meta_info

    ##########################################################################
    # SBML functions
    ##########################################################################

    def _create_sbml_document(self) -> libsbml.SBMLDocument:
        """Create an sbml document, into which sbml information can be written.

        Returns
        -------
        doc : libsbml.Document
        """
        # SBML namespaces
        sbml_ns = libsbml.SBMLNamespaces(3, 2)
        sbml_ns.addPackageNamespace("fbc", 2)
        # SBML document
        doc = libsbml.SBMLDocument(sbml_ns)
        doc.setPackageRequired("fbc", False)
        doc.setSBOTerm(self.meta_info["model"].sbo)
        return doc

    def _create_sbml_model(self, *, doc: libsbml.SBMLDocument) -> libsbml.Model:
        """Create an sbml model.

        Parameters
        ----------
        doc : libsbml.Document

        Returns
        -------
        sbml_model : libsbml.Model
        """
        sbml_model = doc.createModel()
        sbml_model.setId(convert_id_to_sbml(id_=self.meta_info["model"].id, prefix="MODEL"))
        sbml_model.setName(convert_id_to_sbml(id_=self.meta_info["model"].name, prefix="MODEL"))
        sbml_model.setTimeUnits("second")
        sbml_model.setExtentUnits("mole")
        sbml_model.setSubstanceUnits("mole")
        sbml_model_fbc = sbml_model.getPlugin("fbc")
        sbml_model_fbc.setStrict(True)
        return sbml_model

    def _create_sbml_units(self, *, sbml_model: libsbml.Model) -> None:
        """Create sbml units out of the meta_info.

        Parameters
        ----------
        sbml_model : libsbml.Model
        """
        for unit_id, unit in self.meta_info["model"].units.items():
            sbml_definition = sbml_model.createUnitDefinition()
            sbml_definition.setId(unit_id)
            sbml_unit = sbml_definition.createUnit()
            sbml_unit.setKind(unit["kind"])
            sbml_unit.setExponent(unit["exponent"])
            sbml_unit.setScale(unit["scale"])
            sbml_unit.setMultiplier(unit["multiplier"])

    def _create_sbml_compartments(self, *, sbml_model: libsbml.Model) -> None:
        """Create the compartments for the sbml model.

        Since modelbase does not enforce any compartments, so far
        only a cytosol placeholder is introduced.

        Parameters
        ----------
        sbml_model : libsbml.Model
        """
        for compartment_id, compartment in self.meta_info["model"].compartments.items():
            sbml_compartment = sbml_model.createCompartment()
            sbml_compartment.setId(compartment_id)
            sbml_compartment.setName(compartment["name"])
            sbml_compartment.setConstant(compartment["is_constant"])
            sbml_compartment.setSize(compartment["size"])
            sbml_compartment.setSpatialDimensions(compartment["spatial_dimensions"])
            sbml_compartment.setUnits(compartment["units"])

    @abstractmethod
    def _model_to_sbml(self) -> None:
        """Define which methods shall be used for sbml export."""

    def write_sbml_model(self, filename: str = None) -> Optional[str]:
        """Write the model to an sbml file.

        Parameters
        ----------
        filename : str

        Returns
        -------
        doc : libsbml.Document
        """
        doc = self._model_to_sbml()
        if filename is not None:
            libsbml.writeSBMLToFile(doc, filename)
            return None
        model_str: str = libsbml.writeSBMLToString(doc)
        return model_str
