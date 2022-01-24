from __future__ import annotations

__all__ = [
    "LinearRate",
    "LinearLabelModel",
]

import warnings
from typing import Any, Dict, Iterable, List, Tuple, Union, cast

import libsbml
import numpy as np
import numpy.typing as npt
import pandas as pd

from ...core import BaseModel, CompoundMixin, StoichiometricMixin
from ...core.ratemixin import RateMeta
from ...core.utils import convert_id_to_sbml
from . import _AbstractStoichiometricModel


def relative_label_flux(substrate: float, v_ss: float) -> float:
    """Calculate relative label flux."""
    return v_ss * substrate


class LinearRate:
    def __init__(
        self,
        base_name: str,
        substrate: str,
    ):
        self.base_name = base_name
        self.substrate = substrate
        self._y_ss = None
        self._v_ss = None
        self._external_label = None

    def __repr__(self) -> str:
        return repr(self.__dict__)

    def __str__(self) -> str:
        return f"LinearRate(base_name={self.base_name}, substrate={self.substrate}"

    def keys(self) -> List[str]:
        return [
            "base_name",
            "substrate",
        ]

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]


class LinearLabelModel(_AbstractStoichiometricModel):
    """LinearLabelModel."""

    def __init__(
        self,
        compounds: List[str] = None,
        rate_stoichiometries: dict = None,
        rates: dict = None,
        meta_info: dict = None,
    ):
        self.isotopomers: Dict[str, List[str]] = {}
        self.base_rates: Dict[str, set[str]] = {}
        self.rates: Dict[str, LinearRate] = {}
        BaseModel.__init__(self, meta_info=meta_info)
        CompoundMixin.__init__(self, compounds=compounds)
        StoichiometricMixin.__init__(self, rate_stoichiometries=rate_stoichiometries)
        self.meta_info["model"].sbo = "SBO:0000062"  # continuous framework

        if rates is not None:
            for k, v in rates.items():
                self.add_rate(rate_name=k, **v)

    @staticmethod
    def _generate_isotope_labels(*, base_name: str, num_labels: int) -> List[str]:
        """Returns a list of all label isotopomers of the compound."""
        if num_labels > 0:
            return [f"{base_name}__{i}" for i in range(num_labels)]
        raise ValueError(f"Compound {base_name} must have labels")

    def add_compound(self, compound: str, num_labels: int) -> None:  # type: ignore
        """Add a label-containing compound to the model."""
        if compound in self.isotopomers:
            self.remove_compound(compound=compound)
            warnings.warn(f"Overwriting compound {compound}")

        label_names = self._generate_isotope_labels(base_name=compound, num_labels=num_labels)
        self.isotopomers[compound] = label_names
        self._check_and_insert_ids([compound], context="add_compound")

        # Add all labelled compounds
        for isotopomer in label_names:
            super().add_compound(compound=isotopomer)

    def add_compounds(self, compounds: Dict[str, int]) -> None:  # type: ignore
        """Add multiple label-containing compounds to the model.

        Parameters
        ----------
        compounds
            {compound_name: num_labels}
        """
        for compound, num_labels in compounds.items():
            self.add_compound(compound=compound, num_labels=num_labels)

    def remove_compound(self, compound: str) -> None:
        """Remove a compound from the model."""
        isotopomers = self.isotopomers.pop(compound)
        for i in isotopomers:
            super().remove_compound(i)
        self._remove_ids([compound])

    def add_rate(self, rate_name: str, base_name: str, substrate: str, **meta_info) -> None:  # type: ignore
        """Add a rate function to the model.

        Parameters
        ----------
        rate_name
            Name of the rate function plus suffixes
        base_name
            Name of the rate function
        substrate
            Name of the substrate
        meta_info : dict, optional
            Meta info of the rate. Allowed keys are
            {common_name, gibbs0, ec, database_links, notes, sbml_function}

        Warns
        -----
        UserWarning
            If rate is already in the model
        """
        if rate_name in self.rates:
            warnings.warn(f"Overwriting rate {rate_name}", UserWarning)
            self.remove_rate(rate_name=rate_name)

        self.rates[rate_name] = LinearRate(
            base_name=base_name,
            substrate=substrate,
        )
        self.base_rates.setdefault(base_name, set()).add(rate_name)
        self.meta_info.setdefault("rates", {}).setdefault(rate_name, RateMeta(**meta_info))

    def remove_rate(self, rate_name: str) -> None:
        del self.rates[rate_name]

    def get_rate_names(self) -> List[str]:
        return list(self.rates.keys())

    @staticmethod
    def _unpack_stoichiometries(*, stoichiometries: Dict[str, int]) -> Tuple[List[str], List[str]]:
        """Split stoichiometries into substrates and products."""
        substrates = []
        products = []
        for k, v in stoichiometries.items():
            if v < 0:
                substrates.extend([k] * -v)
            else:
                products.extend([k] * v)
        return substrates, products

    @staticmethod
    def _add_label_influx_or_efflux(
        *,
        rate_name: str,
        substrates: List[str],
        products: List[str],
        labelmap: List[int],
    ) -> None:
        # Label outfluxes
        diff = len(substrates) - len(products)
        for _ in range(diff):
            products.append("EXT")

        # Label influxes
        diff = len(labelmap) - len(substrates)
        if diff < 0:
            raise ValueError(f"Labelmap 'missing' {abs(diff)} label(s)")
        warnings.warn(f"Added external label influx for reaction {rate_name}")
        for _ in range(diff):
            substrates.append("EXT")

    @staticmethod
    def _map_substrates_to_labelmap(*, substrates: List[str], labelmap: List[int]) -> List[str]:
        return [substrates[i] for i in labelmap]

    def add_reaction(self, rate_name: str, stoichiometry: Dict[str, int], labelmap: List[int]) -> None:
        """Add a reaction to the model.

        Examples
        --------
        >>> add_reaction(rate_name="v1", stoichiometry={"x": -1, "y": 1}, labelmap=[0, 1])
        """
        if rate_name in self.base_rates:
            warnings.warn(f"Overwriting reaction {rate_name}")
            self.remove_reaction(rate_name=rate_name)

        base_substrates, base_products = self._unpack_stoichiometries(stoichiometries=stoichiometry)
        substrates = [j for i in base_substrates for j in self.isotopomers[i]]
        products = [j for i in base_products for j in self.isotopomers[i]]

        self._add_label_influx_or_efflux(
            rate_name=rate_name,
            substrates=substrates,
            products=products,
            labelmap=labelmap,
        )
        substrates = self._map_substrates_to_labelmap(substrates=substrates, labelmap=labelmap)

        for i, (substrate, product) in enumerate(zip(substrates, products)):
            self.add_stoichiometry(rate_name=f"{rate_name}__{i}", stoichiometry={substrate: -1, product: 1})
            self.add_rate(
                rate_name=f"{rate_name}__{i}",
                base_name=rate_name,
                substrate=substrate,
                **{"sbml_function": f"{rate_name} * {substrate}"},
            )

    def remove_reaction(self, rate_name: str) -> None:
        """Remove a reaction from the model.

        Parameters
        ----------
        rate_name : str
        """
        for rate in self.base_rates[rate_name]:
            self.remove_rate(rate_name=rate)
            self.remove_rate_stoichiometry(rate_name=rate)
        del self.base_rates[rate_name]

    def generate_y0(
        self, initial_labels: Union[Dict[str, int], Dict[str, List[int]]] = None
    ) -> Dict[str, float]:
        """Generate y0 for all isotopomers.

        Examples
        --------
        >>> generate_y0()
        >>> generate_y0(initial_labels={"x": 0})
        >>> generate_y0(initial_labels={"x": [0, 1]})
        """
        y0 = {k: 0.0 for k in self.get_compounds()}
        if initial_labels is not None:
            for base_compound, label_positions in initial_labels.items():
                if isinstance(label_positions, int):
                    label_positions = [label_positions]
                for pos in label_positions:
                    y0[f"{base_compound}__{pos}"] = 1 / len(label_positions)
        return y0

    def _get_fluxes(  # type: ignore
        self,
        *,
        fcd: Dict[str, float],
        v_ss: Dict[str, float],
        external_label: float = 1.0,
    ) -> Dict[str, float]:
        fcd["EXT"] = external_label
        fluxes = {}
        for name, rate in self.rates.items():
            fluxes[name] = relative_label_flux(fcd[rate["substrate"]], v_ss[rate["base_name"]])
        return fluxes

    def get_fluxes_dict(
        self,
        y: Union[Iterable[float], Dict[str, float]],
        v_ss: Dict[str, float],
        external_label: float = 1.0,
    ) -> Dict[str, float]:
        """Calculate the fluxes at time point(s) t."""
        if not isinstance(y, dict):
            y = dict(zip(self.compounds, y))
        return self._get_fluxes(
            fcd=y,  # type: ignore
            v_ss=v_ss,
            external_label=external_label,
        )

    def get_fluxes_array(
        self,
        y: Dict[str, float],
        v_ss: Dict[str, float],
        external_label: float = 1.0,
    ) -> npt.NDArray[np.float64]:
        """Calculate the fluxes at time point(s) t."""
        return np.array(
            list(
                self.get_fluxes_dict(
                    y=y,
                    v_ss=v_ss,
                    external_label=external_label,
                ).values()
            )
        ).T

    def get_fluxes_df(
        self,
        y: Dict[str, float],
        v_ss: Dict[str, float],
        external_label: float = 1.0,
        t: float = 0.0,
    ) -> pd.DataFrame:
        """Calculate the fluxest.

        Parameters
        ----------
        y : Union(dict(str: num), iterable(num))
        t : Union(num, iterable(num))

        Returns
        -------
        fluxes : pandas.DataFrame
        """
        if isinstance(t, (int, float)):
            t_array = [t]
        else:
            t_array = t
        return pd.DataFrame(
            data=self.get_fluxes_dict(y=y, v_ss=v_ss, external_label=external_label),
            index=t_array,
            columns=self.get_rate_names(),
        )

    # This can't get keyword-only arguments, as the integrators are calling it with
    # positional arguments
    def _get_rhs(self, _t: float, y_labels: List[float]) -> List[float]:  # type: ignore[override]
        fcd = dict(zip(self.compounds, y_labels))
        dxdt: Dict[str, float] = {i: 0.0 for i in self.compounds}

        fluxes = self._get_fluxes(fcd=fcd, v_ss=self._v_ss, external_label=self._external_label)
        for compound, isotopomers in self.isotopomers.items():
            for isotomoper in isotopomers:
                for rate, stoich in self.stoichiometries_by_compounds[isotomoper].items():
                    dxdt[isotomoper] += stoich * fluxes[rate] / self._y_ss[compound]
        return list(dxdt.values())

    def get_right_hand_side(
        self,
        y_labels: Union[List[float], Dict[str, float]],
        y_ss: Dict[str, float],
        v_ss: Dict[str, float],
        external_label: float = 1.0,
        t: float = 0.0,
    ) -> Dict[str, float]:
        """Calculate the right hand side of the ODE system.

        Parameters
        ----------
        y_labels
            Relative concentrations of the label positions
        y_ss
            Steady-state concentrations of the base compounds
            obtained from the non-labelled model
        v_ss
            Steady-state fluxes of the base reactions
            obtained from the non-labelled model
        external_label
            Relative concentration of an external label pool
        t
            Time
        """
        self._y_ss = y_ss
        self._v_ss = v_ss
        self._external_label = external_label
        if isinstance(y_labels, dict):
            y_labels = cast(List[float], [y_labels[i] for i in self.compounds])
        return dict(zip(self.compounds, self._get_rhs(_t=t, y_labels=y_labels)))

    ##########################################################################
    # SBML functions
    ##########################################################################

    def _create_sbml_reactions(self, *, sbml_model: libsbml.Model) -> None:
        """Create the reactions for the sbml model.

        Parameters
        ----------
        sbml_model : libsbml.Model
        """
        for rate_id, stoichiometry in self.stoichiometries.items():
            rate = self.meta_info["rates"][rate_id]
            rxn = sbml_model.createReaction()
            rxn.setId(convert_id_to_sbml(id_=rate_id, prefix="RXN"))

            rxn.setFast(False)
            rxn.setReversible(False)

            for compound_id, factor in stoichiometry.items():
                if factor < 0:
                    sref = rxn.createReactant()
                else:
                    sref = rxn.createProduct()
                sref.setSpecies(convert_id_to_sbml(id_=compound_id, prefix="CPD"))
                sref.setStoichiometry(abs(factor))
                sref.setConstant(False)

            kinetic_law = rxn.createKineticLaw()
            kinetic_law.setMath(libsbml.parseL3Formula(rate.sbml_function))

    def _model_to_sbml(self) -> libsbml.SBMLDocument:
        """Export model to sbml."""
        doc = self._create_sbml_document()
        sbml_model = self._create_sbml_model(doc=doc)
        self._create_sbml_units(sbml_model=sbml_model)
        self._create_sbml_compartments(sbml_model=sbml_model)
        self._create_sbml_compounds(sbml_model=sbml_model)
        self._create_sbml_reactions(sbml_model=sbml_model)
        return doc
