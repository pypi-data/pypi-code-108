from __future__ import annotations

__all__ = ["LabelModel"]

import itertools as it
import warnings
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, cast

import libsbml
import numpy as np
import numpy.typing as npt
import pandas as pd

from ...core.compoundmixin import Compound
from ...core.ratemixin import RateMeta
from ...core.utils import convert_id_to_sbml, warning_on_one_line
from .model import Model

warnings.formatwarning = warning_on_one_line  # type: ignore


def total_concentration(*args: float) -> List[npt.NDArray[np.float64]]:
    """Return concentration of all isotopomers.

    Algebraic module function to keep track of the total
    concentration of a compound (so sum of its isotopomers).
    """
    return [np.sum(args, axis=0)]  # type: ignore


class LabelModel(Model):
    """LabelModel."""

    def __init__(
        self,
        parameters: dict = None,
        compounds: List[str] = None,
        algebraic_modules: dict = None,
        rate_stoichiometries: Dict[str, Dict[str, int]] = None,
        rates: dict = None,
        meta_info: dict = None,
    ):
        self.label_compounds: Dict[str, Dict[str, Any]] = {}
        self.nonlabel_compounds: List[str] = []
        self.base_reactions: Dict[str, Dict[str, Any]] = {}
        super().__init__(
            parameters=parameters,
            compounds=compounds,
            algebraic_modules=algebraic_modules,
            rate_stoichiometries=rate_stoichiometries,
            rates=rates,
            meta_info=meta_info,
        )

    @staticmethod
    def _generate_binary_labels(*, base_name: str, num_labels: int) -> List[str]:
        """Create binary label string.

        Returns
        -------
        isotopomers : list(str)
            Returns a list of all label isotopomers of the compound

        Examples
        --------
        >>> _generate_binary_labels(base_name='cpd', num_labels=0)
        ['cpd']

        >>> _generate_binary_labels(base_name='cpd', num_labels=1)
        ['cpd__0', 'cpd__1']

        >>> _generate_binary_labels(base_name='cpd', num_labels=2)
        ['cpd__00', 'cpd__01', 'cpd__10', 'cpd__11']
        """
        if num_labels > 0:
            return [base_name + "__" + "".join(i) for i in it.product(("0", "1"), repeat=num_labels)]
        return [base_name]

    def add_compound(  # type: ignore
        self,
        compound: str,
        is_isotopomer: bool = False,
        **meta_info: Dict[str, Any],
    ) -> None:
        """Add a single compound to the model.

        Parameters
        ----------
        compound
            Name / id of the compound
        is_isotopomer
            Whether the compound is an isotopomer of a base compound
            or a non-label compound
        meta_info
            Meta info of the compound. Available keys are
            {common_name, compartment, formula, charge, gibbs0, smiles, database_links, notes}
        """
        super().add_compound(compound=compound, **meta_info)
        if not is_isotopomer:
            self.nonlabel_compounds.append(compound)

    def _add_base_compound(
        self,
        *,
        base_compound: str,
        num_labels: int,
        label_names: List[str],
        **meta_info: Dict[str, Any],
    ) -> None:
        """Add a base compound of label isotopomer."""
        self.label_compounds[base_compound] = {
            "num_labels": num_labels,
            "isotopomers": label_names,
        }
        self._check_and_insert_ids([base_compound], context="base_compound")
        self.meta_info.setdefault("compounds", {}).setdefault(
            base_compound,
            Compound(**meta_info),  # type: ignore
        )

    def _add_isotopomers(self, *, base_compound: str, label_names: List[str]) -> None:
        # Add all labelled compounds
        for compound in label_names:
            self.add_compound(compound=compound, is_isotopomer=True)
            del self.meta_info["compounds"][compound]

        # Create moiety for total compound concentration
        self.add_algebraic_module(
            module_name=base_compound + "__total",
            function=total_concentration,
            compounds=label_names,
            derived_compounds=[base_compound + "__total"],
            modifiers=None,
            parameters=None,
        )

    def add_label_compound(self, compound: str, num_labels: int, **meta_info: Dict[str, Any]) -> None:
        """Create all label isotopomers and add them as compounds.

        Also create an algebraic module that tracks the total
        concentration of that compound

        Parameters
        ----------
        base_compound
            Base name of the compound
        num_labels
            Number of labels in the compound

        Warns
        -----
        UserWarning
            If compound is already in the model
        """
        if compound in self.label_compounds:
            warnings.warn(f"Overwriting compound {compound}")
            self.remove_label_compound(compound=compound)
        if num_labels == 0:
            self.add_compound(
                compound=compound,
                is_isotopomer=False,
                **meta_info,  # type: ignore
            )
        else:
            label_names = self._generate_binary_labels(base_name=compound, num_labels=num_labels)
            self._add_base_compound(
                base_compound=compound,
                num_labels=num_labels,
                label_names=label_names,
                **meta_info,  # type: ignore
            )
            self._add_isotopomers(base_compound=compound, label_names=label_names)

    def add_label_compounds(
        self,
        compounds: Dict[str, int],
        meta_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add multiple label-containing compounds to the model.

        Parameters
        ----------
        compounds
            {compound: num_labels}

        Examples
        --------
        >>> add_label_compounds({"GAP": 3, "DHAP": 3, "FBP": 6})

        See Also
        --------
        add_label_compound
        """
        meta_info = {} if meta_info is None else meta_info

        for compound, num_labels in compounds.items():
            info = meta_info.get(compound, {})
            self.add_label_compound(compound=compound, num_labels=num_labels, **info)

    def remove_compound(self, compound: str, is_isotopomer: bool = False) -> None:
        """Remove a compound from the model.

        Parameters
        ----------
        compound
        is_isotopomer
            Whether the compound is an isotopomer of a base compound
            or a non-label compound
        """
        super().remove_compound(compound=compound)
        if not is_isotopomer:
            self.nonlabel_compounds.remove(compound)

    def remove_label_compound(self, compound: str) -> None:
        """Remove a label compound from the model."""
        label_compound = self.label_compounds.pop(compound)
        self._remove_ids([compound])
        for key in label_compound["isotopomers"]:
            self.remove_compound(compound=key, is_isotopomer=True)

    def remove_label_compounds(self, compounds: List[str]) -> None:
        """Remove label compounds."""
        for compound in compounds:
            self.remove_label_compound(compound=compound)

    def get_base_compounds(self) -> List[str]:
        """Get all base compounds and non-label compounds."""
        return sorted(list(self.label_compounds) + self.nonlabel_compounds)

    def get_compound_number_of_label_positions(self, compound: str) -> int:
        """Get the number of possible labels positions of a compound."""
        return int(self.label_compounds[compound]["num_labels"])

    def get_compound_isotopomers(self, compound: str) -> List[str]:
        """Get all isotopomers of a compound."""
        return list(self.label_compounds[compound]["isotopomers"])

    def get_compound_isotopomers_with_n_labels(self, compound: str, n_labels: int) -> List[str]:
        """Get all isotopomers of a compound, that have excactly n labels."""
        label_positions = self.label_compounds[compound]["num_labels"]
        label_patterns = [
            ["1" if i in positions else "0" for i in range(label_positions)]
            for positions in it.combinations(range(label_positions), n_labels)
        ]
        return [f"{compound}__{''.join(i)}" for i in label_patterns]

    def get_compound_isotopomer_with_label_position(
        self, base_compound: str, label_position: Union[int, List[int]]
    ) -> str:
        """Get compound isotopomer with a given label position.

        Examples
        --------
        >>> add_label_compounds({"x": 2})
        >>> get_compound_isotopomer_with_label_position(x, 0) -> x__10
        >>> get_compound_isotopomer_with_label_position(x, [0]) -> x__10
        >>> get_compound_isotopomer_with_label_position(x, [0, 1]) -> x__11
        """
        if isinstance(label_position, int):
            label_position = [label_position]
        return f"{base_compound}__" + "".join(
            "1" if idx in label_position else "0"
            for idx in range(self.label_compounds[base_compound]["num_labels"])
        )

    @staticmethod
    def _split_label_string(label: str, *, labels_per_compound: List[int]) -> List[str]:
        """Split label string according to labels given in label list.

        The labels in the label list correspond to the number of
        label positions in the compound.

        Examples
        --------
        >>> _split_label_string(label="01", labels_per_compound=[2])
        ["01"]

        >>> _split_label_string(label="01", labels_per_compound=[1, 1])
        ["0", "1"]

        >>> _split_label_string(label="0011", labels_per_compound=[4])
        ["0011"]

        >>> _split_label_string(label="0011", labels_per_compound=[3, 1])
        ["001", "1"]

        >>> _split_label_string(label="0011", labels_per_compound=[2, 2])
        ["00", "11"]

        >>> _split_label_string(label="0011", labels_per_compound=[1, 3])
        ["0", "011"]
        """
        split_labels = []
        cnt = 0
        for i in range(len(labels_per_compound)):
            split_labels.append(label[cnt : cnt + labels_per_compound[i]])
            cnt += labels_per_compound[i]
        return split_labels

    @staticmethod
    def _map_substrates_to_products(*, rate_suffix: str, labelmap: List[int]) -> str:
        """Map the rate_suffix to products using the labelmap."""
        return "".join([rate_suffix[i] for i in labelmap])

    @staticmethod
    def _unpack_stoichiometries(*, stoichiometries: Dict[str, int]) -> Tuple[List[str], List[str]]:
        """Split stoichiometries into substrates and products.

        Parameters
        ----------
        stoichiometries : dict(str: int)

        Returns
        -------
        substrates : list(str)
        products : list(str)
        """
        substrates = []
        products = []
        for k, v in stoichiometries.items():
            if v < 0:
                substrates.extend([k] * -v)
            else:
                products.extend([k] * v)
        return substrates, products

    def _get_labels_per_compound(self, *, compounds: List[str]) -> List[int]:
        """Get labels per compound.

        This is used for _split_label string. Adds 0 for non-label compounds,
        to show that they get no label."""
        labels_per_compound = []
        for compound in compounds:
            try:
                labels_per_compound.append(self.label_compounds[compound]["num_labels"])
            except KeyError as e:
                if compound not in self.get_compounds():
                    raise KeyError(f"Compound {compound} neither a compound nor a label compound") from e
                labels_per_compound.append(0)
        return labels_per_compound

    @staticmethod
    def _repack_stoichiometries(*, new_substrates: List[str], new_products: List[str]) -> Dict[str, float]:
        """Pack substrates and products into stoichiometric dict."""
        new_stoichiometries: defaultdict[str, int] = defaultdict(int)
        for arg in new_substrates:
            new_stoichiometries[arg] -= 1
        for arg in new_products:
            new_stoichiometries[arg] += 1
        return dict(new_stoichiometries)

    @staticmethod
    def _assign_compound_labels(*, base_compounds: List[str], label_suffixes: List[str]) -> List[str]:
        """Assign the correct suffixes."""
        new_compounds = []
        for i, compound in enumerate(base_compounds):
            if label_suffixes[i] != "":
                new_compounds.append(compound + "__" + label_suffixes[i])
            else:
                new_compounds.append(compound)
        return new_compounds

    def add_algebraic_module(  # type: ignore
        self,
        module_name: str,
        function: Callable,
        compounds: List[str] = None,
        derived_compounds: List[str] = None,
        modifiers: List[str] = None,
        parameters: List[str] = None,
        args: List[str] = None,
    ):
        """Add an algebraic module to the model.

        CAUTION: The Python function of the module has to return an iterable.
        The Python function will get the function arguments in the following order:
        [**compounds, **modifiers, **parameters]

        CAUTION: In a LabelModel context compounds and modifiers will be mapped to
        __total if a label_compound without the isotopomer suffix is supplied.

        Parameters
        ----------
        module_name
            Name of the module
        function
            Python method of the algebraic module
        compounds
            Names of compounds used for module
        derived_compounds
            Names of compounds which are calculated by the module
        modifiers
            Names of compounds which act as modifiers on the module
        parameters
            Names of the parameters which are passed to the function
        meta_info
            Meta info of the algebraic module. Allowed keys are
            {common_name, notes, database_links}

        Warns
        -----
        UserWarning
            If algebraic module is already in the model.

        Examples
        --------
        >>> def rapid_equilibrium(substrate, k_eq)-> None:
        >>>    x = substrate / (1 + k_eq)
        >>>    y = substrate * k_eq / (1 + k_eq)
        >>>    return x, y

        >>> add_algebraic_module(
        >>>     module_name="fast_eq",
        >>>     function=rapid_equilibrium,
        >>>     compounds=["A"],
        >>>     derived_compounds=["X", "Y"],
        >>>     parameters=["K"],
        >>> )
        """
        if compounds is not None:
            compounds = [i + "__total" if i in self.label_compounds else i for i in compounds]
        if modifiers is not None:
            modifiers = [i + "__total" if i in self.label_compounds else i for i in modifiers]
        super().add_algebraic_module(
            module_name=module_name,
            function=function,
            compounds=compounds,
            derived_compounds=derived_compounds,
            modifiers=modifiers,
            parameters=parameters,
            args=args,
        )

    def _get_external_labels(
        self,
        *,
        rate_name: str,
        total_product_labels: int,
        total_substrate_labels: int,
        external_labels: Optional[List[int]],
    ) -> str:
        n_external_labels = total_product_labels - total_substrate_labels
        if n_external_labels > 0:
            if external_labels is None:
                warnings.warn(f"Added external labels for reaction {rate_name}")
                external_label_string = ["1"] * n_external_labels
            else:
                external_label_string = ["0"] * n_external_labels
                for label_pos in external_labels:
                    external_label_string[label_pos] = "1"
            return "".join(external_label_string)
        return ""

    def _add_base_reaction(
        self,
        *,
        rate_name: str,
        function: Callable,
        stoichiometry: Dict[str, int],
        # base_substrates: List[str],
        # base_products: List[str],
        labelmap: List[int],
        external_labels: Optional[str],
        modifiers: Optional[List[str]],
        parameters: Optional[List[str]],
        reversible: bool,
        # dynamic_variables: List[str] = None,
        # args: List[str] = None,
        variants: List[str],
        **meta_info: Dict[str, Any],
    ) -> None:
        # The check isn't as easy.
        # Don't compare to the compounds, probably against base compounds, non-isotopomers and derived compounds?
        # if parameters is None:
        #     parameters = []
        # if modifiers is None:
        #     modifiers = []
        # if reversible:
        #     dynamic_variables = base_substrates + base_products + modifiers
        # else:
        #     dynamic_variables = base_substrates + modifiers
        # self._check_for_existence(
        #     name=rate_name, check_against=self.get_all_compounds(), candidates=dynamic_variables
        # )
        # self._check_for_existence(
        #     name=rate_name, check_against=self.get_parameter_names(), candidates=parameters
        # )
        self.base_reactions[rate_name] = {
            "function": function,
            "stoichiometry": stoichiometry,
            "labelmap": labelmap,
            "external_labels": external_labels,
            "modifiers": modifiers,
            "parameters": parameters,
            "reversible": reversible,
            "variants": variants,
        }
        self.meta_info.setdefault("rates", {}).setdefault(
            rate_name,
            RateMeta(
                **meta_info,  # type: ignore
            ),
        )

    def _create_isotopomer_reactions(
        self,
        *,
        rate_name: str,
        function: Callable,
        labelmap: List[int],
        modifiers: Optional[List[str]],
        parameters: Optional[List[str]],
        reversible: bool,
        # dynamic_variables: List[str],
        # args: List[str],
        external_labels: str,
        total_substrate_labels: int,
        base_substrates: List[str],
        base_products: List[str],
        labels_per_substrate: List[int],
        labels_per_product: List[int],
    ) -> List[str]:
        variants = []
        for rate_suffix in ("".join(i) for i in it.product(("0", "1"), repeat=total_substrate_labels)):
            rate_suffix += external_labels
            # This is the magic
            product_suffix = self._map_substrates_to_products(rate_suffix=rate_suffix, labelmap=labelmap)
            product_labels = self._split_label_string(
                label=product_suffix, labels_per_compound=labels_per_product
            )
            substrate_labels = self._split_label_string(
                label=rate_suffix, labels_per_compound=labels_per_substrate
            )

            new_substrates = self._assign_compound_labels(
                base_compounds=base_substrates, label_suffixes=substrate_labels
            )
            new_products = self._assign_compound_labels(
                base_compounds=base_products, label_suffixes=product_labels
            )
            new_stoichiometry = self._repack_stoichiometries(
                new_substrates=new_substrates, new_products=new_products
            )
            new_rate_name = rate_name + "__" + rate_suffix
            self.add_reaction(
                rate_name=new_rate_name,
                function=function,
                stoichiometry=new_stoichiometry,
                modifiers=modifiers,
                parameters=parameters,
                reversible=reversible,
                # dynamic_variables=dynamic_variables,
                # args=args,
                check_consistency=False,
            )
            del self.meta_info["rates"][new_rate_name]
            variants.append(new_rate_name)
        return variants

    def add_labelmap_reaction(
        self,
        rate_name: str,
        function: Callable,
        stoichiometry: Dict[str, int],
        labelmap: List[int],
        external_labels: Optional[List[int]] = None,
        modifiers: Optional[List[str]] = None,
        parameters: Optional[List[str]] = None,
        reversible: bool = False,
        # dynamic_variables: List[str] = None,
        # args: List[str] = None,
        **meta_info: Dict[str, Any],
    ) -> None:
        """Add a labelmap reaction.

        Parameters
        ----------
        rate_name
            Name of the rate function
        function
            Python method calculating the rate equation
        stoichiometry
            stoichiometry of the reaction
        labelmap
            Mapping of the product label positions to the substrates
        external_labels
            Positions in which external labels are supposed to be inserted
        modifiers
            Names of the modifiers. E.g time.
        parameters
            Names of the parameters
        reversible
            Whether the reaction is reversible.
        meta_info
            Meta info of the rate. Allowed keys are
            {common_name, gibbs0, ec, database_links, notes, sbml_function}

        Examples
        --------
        >>> add_labelmap_reaction(
                rate_name="triose-phosphate-isomerase",
                function=reversible_mass_action,
                labelmap=[2, 1, 0],
                stoichiometry={"GAP": -1, "DHAP": 1},
                parameters=["kf_TPI", "kr_TPI"],
                reversible=True,
            )
        >>> add_labelmap_reaction(
                rate_name="aldolase",
                function=reversible_mass_action_two_one,
                labelmap=[0, 1, 2, 3, 4, 5],
                stoichiometry={"DHAP": -1, "GAP": -1, "FBP": 1},
                parameters=["kf_Ald", "kr_Ald"],
                reversible=True,
            )
        """
        if modifiers is not None:
            modifiers = [i + "__total" if i in self.label_compounds else i for i in modifiers]

        base_substrates, base_products = self._unpack_stoichiometries(stoichiometries=stoichiometry)
        labels_per_substrate = self._get_labels_per_compound(compounds=base_substrates)
        labels_per_product = self._get_labels_per_compound(compounds=base_products)
        total_substrate_labels = sum(labels_per_substrate)
        total_product_labels = sum(labels_per_product)

        if len(labelmap) - total_substrate_labels < 0:
            raise ValueError(f"Labelmap 'missing' {abs(len(labelmap) - total_substrate_labels)} label(s)")

        external_label_str = self._get_external_labels(
            rate_name=rate_name,
            total_product_labels=total_product_labels,
            total_substrate_labels=total_substrate_labels,
            external_labels=external_labels,
        )

        variants = self._create_isotopomer_reactions(
            rate_name=rate_name,
            function=function,
            labelmap=labelmap,
            modifiers=modifiers,
            parameters=parameters,
            reversible=reversible,
            # dynamic_variables=dynamic_variables,
            # args=args,
            external_labels=external_label_str,
            total_substrate_labels=total_substrate_labels,
            base_substrates=base_substrates,
            base_products=base_products,
            labels_per_substrate=labels_per_substrate,
            labels_per_product=labels_per_product,
        )

        self._add_base_reaction(
            rate_name=rate_name,
            function=function,
            # base_substrates=base_substrates,
            # base_products=base_products,
            stoichiometry=stoichiometry,
            labelmap=labelmap,
            external_labels=external_label_str,
            modifiers=modifiers,
            parameters=parameters,
            reversible=reversible,
            # dynamic_variables=dynamic_variables,
            # args=args,
            variants=variants,
            **meta_info,
        )

    def update_labelmap_reaction(
        self,
        rate_name: str,
        function: Optional[Callable] = None,
        stoichiometry: Optional[Dict[str, int]] = None,
        labelmap: Optional[List[int]] = None,
        modifiers: Optional[List[str]] = None,
        parameters: Optional[List[str]] = None,
        reversible: Optional[bool] = None,
        # dynamic_variables: List[str] = None,
        # args: List[str] = None,
    ) -> None:
        """Update an existing labelmap reaction.

        Parameters
        ----------
        rate_name
            Name of the rate function
        function
            Python method calculating the rate equation
        stoichiometry
            stoichiometry of the reaction
        labelmap
            Mapping of the product label positions to the substrates
        external_labels
            Positions in which external labels are supposed to be inserted
        modifiers
            Names of the modifiers. E.g time.
        parameters
            Names of the parameters
        reversible
            Whether the reaction is reversible.
        """
        if function is None:
            function = self.base_reactions[rate_name]["function"]
        if stoichiometry is None:
            stoichiometry = self.base_reactions[rate_name]["stoichiometry"]
        if labelmap is None:
            labelmap = self.base_reactions[rate_name]["labelmap"]
        if modifiers is None:
            modifiers = self.base_reactions[rate_name]["modifiers"]
        if parameters is None:
            parameters = self.base_reactions[rate_name]["parameters"]
        if reversible is None:
            reversible = self.base_reactions[rate_name]["reversible"]

        self.remove_labelmap_reaction(rate_name=rate_name)
        self.add_labelmap_reaction(
            rate_name=rate_name,
            function=function,  # type: ignore
            stoichiometry=stoichiometry,  # type: ignore
            labelmap=labelmap,  # type: ignore
            modifiers=modifiers,
            parameters=parameters,
            reversible=reversible,  # type: ignore
            # dynamic_variables=dynamic_variables,
            # args=args,
        )

    def remove_labelmap_reaction(self, rate_name: str) -> None:
        """Remove all variants of a base reaction.

        Parameters
        ----------
        rate_name : str
            Name of the rate
        """
        self.meta_info["rates"].pop(rate_name)
        base_reaction = self.base_reactions.pop(rate_name)
        for rate in base_reaction["variants"]:
            if rate.startswith(rate_name):
                self.remove_reaction(rate_name=rate)

    def remove_labelmap_reactions(self, rate_names: List[str]) -> None:
        """Remove all variants of a multiple labelmap reactions.

        Parameters
        ----------
        rate_names : iterable(str)

        See Also
        --------
        remove_labelmap_reaction
        """
        for rate_name in rate_names:
            self.remove_labelmap_reaction(rate_name=rate_name)

    def generate_y0(
        self,
        base_y0: Union[List[float], Dict[str, float]],
        label_positions: Dict[str, Union[int, List[int]]] = None,
    ) -> Dict[str, float]:
        """Generate y0 for all isotopomers given a base y0.

        Examples
        --------
        >>> base_y0 = {"GAP": 1, "DHAP": 0, "FBP": 0}
        >>> generate_y0(base_y0=base_y0, label_positions={"GAP": 0})
        >>> generate_y0(base_y0=base_y0, label_positions={"GAP": [0, 1, 2]})
        """
        if label_positions is None:
            label_positions = {}
        if not isinstance(base_y0, dict):
            base_y0 = dict(zip(self.label_compounds, base_y0))

        y0 = dict(zip(self.get_compounds(), np.zeros(len(self.get_compounds()))))
        for base_compound, concentration in base_y0.items():
            label_position = label_positions.get(base_compound, None)
            if label_position is None:
                try:
                    y0[self.label_compounds[base_compound]["isotopomers"][0]] = concentration
                except KeyError:  # non label compound
                    y0[base_compound] = concentration
            else:
                if isinstance(label_position, int):
                    label_position = [label_position]
                suffix = "__" + "".join(
                    "1" if idx in label_position else "0"
                    for idx in range(self.label_compounds[base_compound]["num_labels"])
                )
                y0[base_compound + suffix] = concentration
        return y0

    def get_total_fluxes(
        self,
        rate_base_name: str,
        y: Union[Dict[str, float], Dict[str, List[float]]],
        t: Union[float, List[float]] = 0,
    ) -> npt.NDArray[np.float64]:
        """Get total fluxes of a base rate.

        Parameters
        ----------
        rate_base_name : str
        y : Union(iterable(num), dict(str: num))
        t : Union(num, iterable(num))

        Returns
        -------
        fluxes : numpy.array
        """
        rates = [i for i in self.rates if i.startswith(rate_base_name + "__")]
        return cast(
            npt.NDArray[np.float64],
            self.get_fluxes_df(y=y, t=t)[rates].sum(axis=1).values,  # type: ignore
        )

    def _create_label_scope_seed(
        self, *, initial_labels: Union[Dict[str, int], Dict[str, List[int]]]
    ) -> Dict[str, int]:
        """Create initial label scope seed."""

        # initialise all compounds with 0 (no label)
        labelled_compounds = {compound: 0 for compound in self.get_compounds()}

        # Set all unlabelled compounds to 1
        for name, compound in self.label_compounds.items():
            num_labels = compound["num_labels"]
            labelled_compounds[f"{name}__{'0' * num_labels}"] = 1
        # Also set all non-label compounds to 1
        for name in self.nonlabel_compounds:
            labelled_compounds[name] = 1
        # Set initial label
        for i in [
            self.get_compound_isotopomer_with_label_position(
                base_compound=base_compound, label_position=label_position
            )
            for base_compound, label_position in initial_labels.items()
        ]:
            labelled_compounds[i] = 1
        return labelled_compounds

    def get_label_scope(
        self,
        initial_labels: Union[Dict[str, int], Dict[str, List[int]]],
    ) -> Dict[int, set[str]]:
        """Return all label positions that can be reached step by step.

        Parameters
        ----------
        initial_labels : dict(str: num)

        Returns
        -------
        label_scope : dict{step : set of new positions}

        Examples
        --------
        >>> l.get_label_scope({"x": 0})
        >>> l.get_label_scope({"x": [0, 1], "y": 0})
        """
        labelled_compounds = self._create_label_scope_seed(initial_labels=initial_labels)
        new_labels = set("non empty entry to not fulfill while condition")
        # Loop until no new labels are inserted
        loop_count = 0
        result = {}
        while new_labels != set():
            new_cpds = labelled_compounds.copy()
            for rec, cpd_dict in self.get_stoichiometries().items():
                # Isolate substrates
                cpds = [i for i, j in cpd_dict.items() if j < 0]
                # Count how many of the substrates are 1
                i = 0
                for j in cpds:
                    i += labelled_compounds[j]
                # If all substrates are 1, set all products to 1
                if i == len(cpds):
                    for cpd in self.get_stoichiometries()[rec]:
                        new_cpds[cpd] = 1
                if self.rates[rec]["reversible"]:
                    # Isolate substrates
                    cpds = [i for i, j in cpd_dict.items() if j > 0]
                    # Count how many of the substrates are 1
                    i = 0
                    for j in cpds:
                        i += labelled_compounds[j]
                    # If all substrates are 1, set all products to 1
                    if i == len(cpds):
                        for cpd in self.get_stoichiometries()[rec]:
                            new_cpds[cpd] = 1
            # Isolate "old" labels
            s1 = pd.Series(labelled_compounds)
            s1 = cast(pd.Series, s1[s1 == 1])
            # Isolate new labels
            s2 = pd.Series(new_cpds)
            s2 = cast(pd.Series, s2[s2 == 1])
            # Find new labels
            new_labels = cast(Set[str], set(s2.index).difference(set(s1.index)))
            # Break the loop once no new labels can be found
            if new_labels == set():
                break
            labelled_compounds = new_cpds
            result[loop_count] = new_labels
            loop_count += 1
        return result

    ##########################################################################
    # Model conversion functions
    ##########################################################################

    def _map_label_compound_to_compound(self, *, compound: str) -> str:
        if compound in self.nonlabel_compounds:
            return compound
        return compound.rsplit("__")[0]

    def to_model(self) -> Model:
        """Convert LabelModel to Model."""
        m = Model()
        m.add_parameters(self.parameters)
        m.add_compounds(list(self.label_compounds.keys()))
        m.add_compounds(self.nonlabel_compounds)

        for module_name, module in self.algebraic_modules.items():
            if not module_name.endswith("__total"):
                module_ = dict(module)
                module_["compounds"] = [
                    self._map_label_compound_to_compound(compound=i) for i in module["compounds"]
                ]
                module_["derived_compounds"] = [
                    self._map_label_compound_to_compound(compound=i) for i in module["derived_compounds"]
                ]
                module_["modifiers"] = [
                    self._map_label_compound_to_compound(compound=i) for i in module["modifiers"]
                ]
                m.add_algebraic_module(module_name=module_name, **module_)

        for rate_name, reaction in self.base_reactions.items():
            reaction = reaction.copy()
            reaction["stoichiometry"] = {
                self._map_label_compound_to_compound(compound=k): v
                for k, v in reaction["stoichiometry"].items()
            }
            reaction["modifiers"] = [
                self._map_label_compound_to_compound(compound=i) for i in reaction["modifiers"]
            ]
            del reaction["labelmap"]
            del reaction["external_labels"]
            del reaction["variants"]
            m.add_reaction(rate_name=rate_name, **reaction)
        return m

    ##########################################################################
    # SBML functions
    ##########################################################################

    def _add_sbml_compound(
        self,
        *,
        sbml_model: libsbml.Model,
        compound_id: str,
        common_name: str,
        compartment: str,
        charge: int,
        formula: str,
    ) -> None:
        cpd = sbml_model.createSpecies()
        cpd.setId(convert_id_to_sbml(id_=compound_id, prefix="CPD"))
        if common_name is not None:
            cpd.setName(common_name)
        cpd.setConstant(False)
        cpd.setBoundaryCondition(False)
        cpd.setHasOnlySubstanceUnits(False)
        cpd.setCompartment(compartment)

        cpd_fbc = cpd.getPlugin("fbc")
        if charge is not None:
            cpd_fbc.setCharge(int(charge))
        if formula is not None:
            cpd_fbc.setChemicalFormula(formula)

    def _create_sbml_compounds(self, *, sbml_model: libsbml.Model) -> None:
        """Create the compounds for the sbml model.

        Parameters
        ----------
        sbml_model : libsbml.Model
        """
        for base_compound_id, base_compound in self.label_compounds.items():
            compound = self.meta_info["compounds"][base_compound_id]
            common_name = compound.common_name
            charge = compound.charge
            formula = compound.formula
            compartment = compound.compartment

            for compound_id in base_compound["isotopomers"]:
                self._add_sbml_compound(
                    sbml_model=sbml_model,
                    compound_id=compound_id,
                    common_name=common_name,
                    compartment=compartment,
                    charge=charge,
                    formula=formula,
                )

        for compound_id in self.nonlabel_compounds:
            compound = self.meta_info["compounds"][compound_id]
            common_name = compound.common_name
            charge = compound.charge
            formula = compound.formula
            compartment = compound.compartment
            self._add_sbml_compound(
                sbml_model=sbml_model,
                compound_id=compound_id,
                common_name=common_name,
                compartment=compartment,
                charge=charge,
                formula=formula,
            )

    def _create_sbml_reactions(self, *, sbml_model: libsbml.Model) -> None:
        """Create the reactions for the sbml model.

        Parameters
        ----------
        sbml_model : libsbml.Model
        """
        for base_rate_id, base_rate in self.base_reactions.items():
            rate = self.meta_info["rates"][base_rate_id]
            name = rate.common_name
            # function = rate.sbml_function
            reversible = base_rate["reversible"]

            for rate_id in base_rate["variants"]:
                stoichiometry = self.stoichiometries[rate_id]
                rxn = sbml_model.createReaction()
                rxn.setId(convert_id_to_sbml(id_=rate_id, prefix="RXN"))
                if name:
                    rxn.setName(name)
                rxn.setFast(False)
                rxn.setReversible(reversible)

                for compound_id, factor in stoichiometry.items():
                    if factor < 0:
                        sref = rxn.createReactant()
                    else:
                        sref = rxn.createProduct()
                    sref.setSpecies(convert_id_to_sbml(id_=compound_id, prefix="CPD"))
                    sref.setStoichiometry(abs(factor))
                    sref.setConstant(False)

                for compound in self.rates[rate_id]["modifiers"]:
                    sref = rxn.createModifier()
                    sref.setSpecies(convert_id_to_sbml(id_=compound, prefix="CPD"))

                # if function is not None:
                #     kinetic_law = rxn.createKineticLaw()
                #     kinetic_law.setMath(libsbml.parseL3Formula(function))
