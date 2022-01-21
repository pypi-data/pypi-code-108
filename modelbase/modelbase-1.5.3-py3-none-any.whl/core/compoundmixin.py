from __future__ import annotations

__all__ = [
    "Compound",
    "CompoundMixin",
]

import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

import libsbml

from .basemodel import BaseModel
from .utils import convert_id_to_sbml, warning_on_one_line

warnings.formatwarning = warning_on_one_line  # type: ignore


@dataclass
class Compound:
    """Meta-info container for compounds."""

    common_name: Optional[str] = None
    compartment: Optional[str] = "c"
    unit: Optional[str] = None
    formula: Optional[str] = None
    charge: Optional[float] = None
    gibbs0: Optional[float] = None
    smiles: Optional[str] = None
    database_links: dict = field(default_factory=dict)
    notes: dict = field(default_factory=dict)


class CompoundMixin(BaseModel):
    """Mixin for compound functionality."""

    def __init__(self, compounds: List[str] = None) -> None:
        self.compounds: List[str] = []
        if compounds is not None:
            self.add_compounds(compounds=compounds)

    ##########################################################################
    # Compound functions
    ##########################################################################

    def add_compound(
        self,
        compound: str,
        **meta_info: Dict[str, Any],
    ) -> None:
        """Add a compound to the model.

        Parameters
        ----------
        compound
            Name / id of the compound
        meta_info
            Meta info of the compound. Available keys are
            {common_name, compartment, formula, charge, gibbs0, smiles, database_links, notes}
        """
        if not isinstance(compound, str):
            raise TypeError("The compound name should be string")
        if compound == "time":
            raise KeyError("time is a protected variable for time")
        else:
            if compound in self.compounds:
                warnings.warn(f"Overwriting compound {compound}")
                self.remove_compound(compound=compound)
            self.compounds.append(compound)
            self.meta_info.setdefault("compounds", {}).setdefault(
                compound,
                Compound(**meta_info),  # type: ignore
            )
            self._check_and_insert_ids([compound], context="add_compound")

    def add_compounds(self, compounds: List[str], meta_info: Optional[Dict[str, Any]] = None) -> None:
        """Add multiple compounds to the model.

        See Also
        --------
        add_compound
        """
        meta_info = {} if meta_info is None else meta_info
        for compound in compounds:
            try:
                info = meta_info[compound]
            except KeyError:
                info = {}
            self.add_compound(compound=compound, **info)

    def update_compound_meta_info(self, compound: str, meta_info: dict) -> None:
        """Update meta info of a compound.

        Parameters
        ----------
        compound : str
            Name / id of the compound
        meta_info : dict, optional
            Meta info of the compound. Available keys are
            {common_name, compartment, formula, charge, gibbs0, smiles, database_links, notes}
        """
        self.update_meta_info(component="compounds", meta_info={compound: meta_info})

    def remove_compound(self, compound: str) -> None:
        """Remove a compound from the model"""
        self.compounds.remove(compound)
        self._remove_ids([compound])
        try:
            del self.meta_info["compounds"][compound]
        except KeyError:
            pass

    def remove_compounds(self, compounds: Iterable[str]) -> None:
        """Remove compounds from the model"""
        for compound in compounds:
            self.remove_compound(compound=compound)

    def _get_all_compounds(self) -> List[str]:
        """Get all compounds from the model.

        If used together with the algebraic mixin, this will return
        compounds + derived_compounds. Here it's just for API stability
        """
        return list(self.compounds)

    def get_compounds(self) -> List[str]:
        """Get the compounds from the model"""
        return list(self.compounds)

    ##########################################################################
    # Source code functions
    ##########################################################################

    def _generate_compounds_source_code(self, *, include_meta_info: bool = True) -> str:
        """Generate modelbase source code for compounds.

        This is mainly used for the generate_model_source_code function.

        Parameters
        ----------
        include_meta_info : bool
            Whether to include the compounds meta info

        Returns
        -------
        compounds_modelbase_code : str
            Source code generating the modelbase compounds
        """
        if include_meta_info:
            meta_info = self._get_nonzero_meta_info(component="compounds")
            if bool(meta_info):
                return f"m.add_compounds(compounds={repr(self.compounds)}, meta_info={meta_info})"
        return f"m.add_compounds(compounds={repr(self.compounds)})"

    ##########################################################################
    # SBML functions
    ##########################################################################

    def _create_sbml_compounds(self, *, sbml_model: libsbml.Model) -> None:
        """Create the compounds for the sbml model.

        Parameters
        ----------
        sbml_model : libsbml.Model
        """
        for compound_id in self.get_compounds():
            compound = self.meta_info["compounds"][compound_id]
            cpd = sbml_model.createSpecies()
            cpd.setId(convert_id_to_sbml(id_=compound_id, prefix="CPD"))
            common_name = compound.common_name
            if common_name is not None:
                cpd.setName(common_name)
            cpd.setConstant(False)
            cpd.setBoundaryCondition(False)
            cpd.setHasOnlySubstanceUnits(False)
            cpd.setCompartment(compound.compartment)

            cpd_fbc = cpd.getPlugin("fbc")
            charge = compound.charge
            if charge is not None:
                cpd_fbc.setCharge(int(charge))
            formula = compound.formula
            if formula is not None:
                cpd_fbc.setChemicalFormula(formula)
