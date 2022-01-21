"""The main model class, with which users are supposed to interface."""
from __future__ import annotations

__all__ = ["Model"]

import copy
import dataclasses
import json
import pickle
import re
import warnings
from collections import defaultdict
from pathlib import Path
from typing import (
    Any,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Pattern,
    Set,
    Tuple,
    Union,
    cast,
)

import cobra
import cycparser
import libsbml
import numpy as np
import pandas as pd
import yaml

from .. import topological
from ..utils import get_temporary_directory
from ..utils.sbml import export_model as _export_model
from .compound import Compound
from .constants import BIOMASS_TEMPLATES
from .kinetic_data import KineticData
from .monomer import Monomer
from .reaction import Reaction

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import modelbase.ode as ode
    from modelbase.ode import ratelaws as rl


@dataclasses.dataclass
class SearchResult:
    reactions: List[str]
    compounds: List[str]


class Model:
    """The main model class."""

    def __init__(
        self,
        compounds: Iterable[Compound] | None = None,
        reactions: Iterable[Reaction] | None = None,
        compartments: Dict[str, str] | None = None,
        objective: Dict[str, float] | None = None,
        minimal_seed: Set[str] | None = None,
        cofactor_pairs: Dict[str, str] | None = None,
        monomers: Dict[str, Monomer] | None = None,
        # gpr_annotations: Dict[str, List[Set[str]]] | None = None,
        # kinetic_data: Dict[str, Dict[str, KineticData]] | None = None,
        name: str | None = None,
    ) -> None:
        self.name: str = name if name is not None else "Model"
        self.compartments: Dict[str, str] = {}
        self.compounds: Dict[str, Compound] = {}
        self.base_compounds: Dict[str, Set[str]] = {}
        self.reactions: Dict[str, Reaction] = {}
        self.base_reactions: Dict[str, Set[str]] = {}
        self.variant_reactions: Dict[str, Set[str]] = {}
        self.pathways: Dict[str, Set[str]] = {}
        self.objective: Dict[str, float] = {}
        self.cofactor_pairs: Dict[str, str] = {}
        self.minimal_seed = set() if minimal_seed is None else minimal_seed
        self.monomers: Dict[str, Monomer] = {}
        # self.kinetic_data: Dict[str, Dict[str, KineticData]] = {}
        # self.gpr_annotations: Dict[str, List[Set[str]]] = {}

        # Filled by routines
        self._compound_types: Dict[str, Set[str]] = {}
        self._reaction_types: Dict[str, Set[str]] = {}
        self._base_cofactor_pairs: Dict[str, str] = {}
        # Temporary containers
        self._duplicate_reactions: Set[str] = set()

        if compartments is not None:
            self.add_compartments(compartments=compartments)
        if compounds is not None:
            self.add_compounds(compounds=compounds)
        if cofactor_pairs is not None:
            for strong, weak in cofactor_pairs.items():
                self.add_cofactor_pair(strong, weak)
        if reactions is not None:
            self.add_reactions(reactions=reactions)
        if objective is not None:
            self.set_objective(objective=objective)
        if monomers is not None:
            self.add_monomers(monomers)
        # if gpr_annotations is not None:
        #     self.add_gpr_annotations(gpr_annotations)
        # if kinetic_data is not None:
        #     self.add_kinetic_data(kinetic_data)

    def __repr__(self) -> str:
        s = f"Model: {self.name}\n"
        s += f"    compounds: {len(self.compounds)}\n"
        s += f"    reactions: {len(self.reactions)}\n"
        return s

    def __str__(self) -> str:
        s = f"Model: {self.name}\n"
        s += f"    compounds: {len(self.compounds)}\n"
        s += f"    reactions: {len(self.reactions)}\n"
        return s

    def __enter__(self) -> "Model":
        """Return and save a copy for context manager."""
        self._copy = self.copy()
        return self.copy()

    def __exit__(
        self,
        exception_type: Any,
        exception_value: Any,
        exception_traceback: Any,
    ) -> None:
        """Restore any changes made to the model."""
        self.__dict__ = self._copy.__dict__

    def __add__(self, other: object) -> "Model":
        if not isinstance(other, Model):
            return NotImplemented
        m1 = self.copy()
        m1.add_compartments(other.compartments)
        m1.add_compounds(other.compounds.values())
        m1.add_reactions(other.reactions.values())
        return m1

    def __iadd__(self, other: object) -> "Model":
        if not isinstance(other, Model):
            return NotImplemented
        self.add_compartments(other.compartments)
        self.add_compounds(other.compounds.values())
        self.add_reactions(other.reactions.values())
        return self

    def __sub__(self, other: object) -> "Model":
        if not isinstance(other, Model):
            return NotImplemented
        m = self.copy()
        m.remove_compartments([k for k in self.compartments.keys() if k in other.compartments])
        m.remove_compounds([k for k in self.compounds.keys() if k in other.compounds])
        m.remove_reactions([k for k in self.reactions.keys() if k in other.reactions])
        return m

    def __isub__(self, other: object) -> "Model":
        if not isinstance(other, Model):
            return NotImplemented
        self.remove_compartments([k for k in self.compartments.keys() if k in other.compartments])
        self.remove_compounds([k for k in self.compounds.keys() if k in other.compounds])
        self.remove_reactions([k for k in self.reactions.keys() if k in other.reactions])
        return self

    def __and__(self, other: object) -> "Model":
        if not isinstance(other, Model):
            return NotImplemented
        m = self.copy()
        m.add_compartments({k: v for k, v in self.compartments.items() if k in other.compartments})
        m.add_compounds([v for k, v in self.compounds.items() if k in other.compounds])
        m.add_reactions([v for k, v in self.reactions.items() if k in other.reactions])
        return m

    def __or__(self, other: object) -> "Model":
        if not isinstance(other, Model):
            return NotImplemented
        return self + other

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Model):
            return NotImplemented
        return all(getattr(self, i) == getattr(other, i) for i in self.__dict__)

    def copy(self) -> "Model":
        """Create a deepcopy of the reaction.

        While this is more costly than shallow copies, it takes away
        the hassle of always keeping track if a shallow copy is what
        you want at the moment. So it's mostly for me not getting
        confused ;)

        Returns
        -------
        self: moped.Model
        """
        return copy.deepcopy(self)

    def add_compartment(self, compartment_id: str, compartment_suffix: str) -> None:
        """Add a compartment to the model.

        Examples
        --------
        model.add_compartment(compartment_id='cytosol', compartment_suffix='c')
        """
        self.compartments[compartment_id] = compartment_suffix

    def add_compartments(self, compartments: Dict[str, str]) -> None:
        """Add multiple compartments to the model.

        Examples
        --------
        model.add_compartments(compartments={'cytosol': 'c'})
        """
        for compartment_id, compartment_suffix in compartments.items():
            self.add_compartment(
                compartment_id=compartment_id,
                compartment_suffix=compartment_suffix,
            )

    def remove_compartment(self, compartment: str) -> None:
        del self.compartments[compartment]

    def remove_compartments(self, compartments: Iterable[str]) -> None:
        for i in compartments:
            self.remove_compartment(compartment=i)

    def add_monomers(self, monomers: Dict[str, Monomer]) -> None:
        self.monomers.update(monomers)

    # def add_gpr_annotations(self, annotations: Dict[str, List[Set[str]]]) -> None:
    #     self.gpr_annotations.update(annotations)

    # def add_kinetic_data(self, kinetic_data: Dict[str, Dict[str, KineticData]]) -> None:
    #     for rxn, d in kinetic_data.items():
    #         for enzyme, data in d.items():
    #             self.kinetic_data.setdefault(rxn, {}).setdefault(enzyme, data)

    ##########################################################################
    # Utils
    ##########################################################################

    def _add_compartment_suffix(self, object_id: str, compartment_id: str) -> str:
        """Add a compartment suffix (e.g. _e for extracellular) to the id.

        Raises
        ------
        KeyError
            If compartment does not exist
        """
        suffix = self.compartments[compartment_id]
        if suffix != "":
            return object_id + f"_{suffix}"
        return object_id

    @staticmethod
    def _strip_compartment_suffix(object_id: str, compartment_pattern: Pattern[str]) -> str:
        """Split the compartment string from an object_id."""
        return re.sub(compartment_pattern, "", object_id)

    ##########################################################################
    # Creation routines
    ##########################################################################

    def _fix_light_reaction_mass_balance(self) -> None:
        """This one is really weird.
        Memote requires us to give light a mass and then add another compound,
        such that we can mass-balance the reactions. Yes.
        """
        if (cpd := self.compounds.get("Light_c")) is not None:
            if "EXTRACELLULAR" not in self.compartments:  # can happen in rare cases
                self.compartments["EXTRACELLULAR"] = "e"
            cpd.formula = {"Photon": 1}
            self.add_compound(
                Compound(
                    base_id="Light_used",
                    compartment="EXTRACELLULAR",
                    id="Light_used_e",
                    charge=0,
                    formula={"Photon": 1},
                )
            )
            self.add_efflux("Light_used_e", "EXTRACELLULAR")
            # for rxn_id in self.pathways.get("PWY-101", set()):
            # reaction = self.reactions[rxn_id]
            for reaction in self.reactions.values():
                if "Light_c" in reaction.stoichiometries:
                    reaction.stoichiometries["Light_used_e"] = -1 * reaction.stoichiometries["Light_c"]

    def _fix_periplasm_proton_gradient(self) -> None:
        """Set reactions that do not match proton gradient criteria to irreversible.

        The criteria are the following:
        - All reactions of the following types are always kept
            TR-13 (Transport Energized by Phosphoanhydride-Bond Hydrolysis)
            TR-15 (Transport Energized by Decarboxylation)
            Membrane-Protein-Modification-Reactions
            Electron-Transfer-Reactions
        - If a reaction otherwise transports protons inside of the periplasm it is
         usually of the type
            TR-12 (Transport Energized by the Membrane Electrochemical Gradient)
        Keeping those reactions leads to thermodynamically infeasible loops, therefore
        they are reverted to a way that they only transport protons to the cytosol
        and are irreversible.
        """
        if "PERIPLASM" in self.get_model_compartment_ids():
            periplasm_recs = [
                self.reactions[i] for i in self.get_transport_reactions(compartment_id="PERIPLASM")
            ]
            proton_translocators = {i.id for i in periplasm_recs if "PROTON_p" in i.stoichiometries}
            try:
                tr13 = self.get_reactions_of_type(reaction_type="TR-13")
            except KeyError:
                tr13 = set()
            try:
                tr15 = self.get_reactions_of_type(reaction_type="TR-15")
            except KeyError:
                tr15 = set()
            try:
                mpmr = self.get_reactions_of_type(reaction_type="Membrane-Protein-Modification-Reactions")
            except KeyError:
                mpmr = set()
            try:
                etr = self.get_reactions_of_type(reaction_type="Electron-Transfer-Reactions")
            except KeyError:
                etr = set()
            to_fix = proton_translocators.difference(tr13 | tr15 | etr | mpmr)
            for reaction_id in to_fix:
                reaction = self.reactions[reaction_id]
                if reaction.stoichiometries["PROTON_p"] > 0:
                    reaction.reverse_stoichiometry()
                reaction.make_irreversible()

    def _move_electron_transport_cofactors_to_cytosol(self) -> None:
        """Move all periplasmatic electron transport cofactors into cytosol.

        This is done to keep the connectivity of the network.
        """
        cofactors = {
            "Reduced-ferredoxins_p": "Reduced-ferredoxins_c",
            "Oxidized-ferredoxins_p": "Oxidized-ferredoxins_c",
            "Cytochromes-C-Reduced_p": "Cytochromes-C-Reduced_c",
            "Cytochromes-C-Oxidized_p": "Cytochromes-C-Oxidized_c",
            "NADPH_p": "NADPH_c",
            "NADP_p": "NADP_c",
            "NAD_p": "NAD_c",
            "ATP_p": "ATP_c",
            "ADP_p": "ADP_c",
        }

        try:
            etr_reactions = self.get_reactions_of_type(reaction_type="Electron-Transfer-Reactions")
        except KeyError:
            pass
        else:
            for reaction_id in tuple(etr_reactions):
                reaction = copy.deepcopy(self.reactions[reaction_id])
                if "PERIPLASM" in cast(str, reaction.compartment):
                    changed_cpds = False
                    for compound_id in tuple(reaction.stoichiometries):
                        if compound_id in cofactors:
                            reaction.stoichiometries[cofactors[compound_id]] = reaction.stoichiometries.pop(
                                compound_id
                            )
                            changed_cpds = True
                    if changed_cpds:
                        self.remove_reaction(
                            reaction_id=reaction_id,
                            remove_empty_references=False,
                        )
                        self._move_reaction_to_other_compartment(reaction)

    def _move_reaction_to_other_compartment(self, reaction: Reaction) -> None:
        reaction.id = cast(str, reaction.base_id)
        if (count := reaction._var) is not None:
            reaction.id += f"__var__{count}"
        new_compartments = tuple(
            sorted({cast(str, self.compounds[i].compartment) for i in reaction.stoichiometries})
        )
        if len(new_compartments) == 1:
            compartment = new_compartments[0]
            reaction.compartment = compartment
            reaction.transmembrane = False
            reaction.id += self._add_compartment_suffix(object_id="", compartment_id=compartment)
        else:
            reaction.compartment = new_compartments
            reaction.transmembrane = True
            for compartment_id in reaction.compartment:
                reaction.id += self._add_compartment_suffix(object_id="", compartment_id=compartment_id)
        self.add_reaction(reaction=reaction)

    def _repair_photosynthesis_reactions(self) -> None:
        """Switch the photosynthesis reactions proton compartments.

        The way the photosynthesis reactions are currently annotated and parsed,
        they will transport protons out of the periplasm, while they are
        actually doing the opposite.
        """
        try:
            for reaction_id in list(self.pathways["PWY-101"]):
                reaction = copy.deepcopy(self.reactions[reaction_id])
                if reaction.transmembrane:
                    self.remove_reaction(reaction_id, remove_empty_references=False)
                    st = reaction.stoichiometries
                    in_compartment, out_compartment = cast(Tuple[str, str], reaction.compartment)
                    in_proton_name = self._add_compartment_suffix(
                        object_id="PROTON", compartment_id=in_compartment
                    )
                    out_proton_name = self._add_compartment_suffix(
                        object_id="PROTON", compartment_id=out_compartment
                    )
                    try:
                        in_protons = st.pop(in_proton_name)
                        in_error = False
                    except KeyError:
                        in_error = True
                    try:
                        out_protons = st.pop(out_proton_name)
                        out_error = False
                    except KeyError:
                        out_error = True
                    if not in_error:
                        st[out_proton_name] = in_protons  # type: ignore
                    if not out_error:
                        st[in_proton_name] = out_protons  # type: ignore
                    self._move_reaction_to_other_compartment(reaction)
        except KeyError:
            pass

    def read_from_pgdb(
        self,
        pgdb_path: Union[str, Path],
        move_electron_transport_cofactors_to_cytosol: bool = True,
        repair_photosynthesis_reactions: bool = True,
        fix_periplasm_proton_gradient: bool = True,
        fix_light_reaction_mass_balance: bool = True,
        remove_unused_compounds: bool = True,
        compartment_map: Dict[str, str] | None = None,
        compartment_suffixes: Dict[str, str] | None = None,
        type_map: Dict[str, str] | None = None,
    ) -> None:
        parse_results = cycparser.parse_and_repair_pgdb(
            Path(pgdb_path),
            compartment_map=compartment_map,
            type_map=type_map,
            manual_additions=None,
            compartment_suffixes=compartment_suffixes,
        )
        parse_compounds = parse_results.compounds
        parse_reactions = parse_results.reactions
        parse_compartments = parse_results.compartments
        parse_gpr_annotations = parse_results.gpr_annotations
        parse_kinetic_data = parse_results.kinetic_data
        parse_monomers = parse_results.monomers

        moped_kinetic_data = {
            k: {k2: KineticData(v2.km, v2.kcat, v2.vmax)}
            for k, v in parse_kinetic_data.items()
            for k2, v2 in v.items()
        }

        moped_compounds = [
            Compound(
                base_id=v.base_id,
                compartment=v.compartment,
                formula=v.formula,
                charge=v.charge,
                name=v.name,
                gibbs0=v.gibbs0,
                smiles=v.smiles,
                database_links=v.database_links,
                types=v.types,
                id=v.id,
            )
            for v in parse_compounds.values()
        ]
        moped_reactions = [
            Reaction(
                base_id=v.base_id,
                id=v.id,
                stoichiometries=v.stoichiometries,
                compartment=v.compartment,
                name=v.name,
                bounds=v.bounds,
                gibbs0=v.gibbs0,
                ec=v.ec,
                types=v.types,
                pathways=v.pathways,
                database_links=v.database_links,
                transmembrane=v.transmembrane,
                kinetic_data=moped_kinetic_data.get(v.base_id, {}),
                gpr_annotation=parse_gpr_annotations.get(v.base_id, []),
                _var=v._var,
            )
            for v in parse_reactions.values()
        ]
        moped_monomers = {
            k: Monomer(id=k, sequence=v.sequence, database_links=v.database_links)
            for k, v in parse_monomers.items()
        }
        self.compartments = parse_compartments
        self.add_compounds(moped_compounds)

        for strong_cofactor_base_id, weak_cofactor_base_id in {
            "ATP": "ADP",
            "GTP": "GDP",
            "NADH": "NAD",
            "NADPH": "NADP",
            "10-FORMYL-THF": "THF",
            "METHYLENE-THF": "THF",
            "5-METHYL-THF": "THF",
            "ACETYL-COA": "CO-A",
            "Donor-H2": "Acceptor",
            "Reduced-ferredoxins": "Oxidized-ferredoxins",
            "Red-NADPH-Hemoprotein-Reductases": "Ox-NADPH-Hemoprotein-Reductases",
            "Cytochromes-C-Reduced": "Cytochromes-C-Oxidized",
            "Plastocyanin-Reduced": "Oxidized-Plastocyanins",
            "ETF-Reduced": "ETF-Oxidized",
            "Red-Thioredoxin": "Ox-Thioredoxin",
            "CPD-12829": "PLASTOQUINONE-9",
        }.items():
            self.add_cofactor_pair(
                strong_cofactor_base_id=strong_cofactor_base_id,
                weak_cofactor_base_id=weak_cofactor_base_id,
            )

        self.add_reactions(moped_reactions)

        self.add_minimal_seed(
            compound_ids={
                "WATER_c",
                "PROTON_c",
                "OXYGEN-MOLECULE_c",
                "CARBON-DIOXIDE_c",
                "Pi_c",
                "MN+2_c",
                "ZN+2_c",
                "CU+2_c",
                "CA+2_c",
                "SULFATE_c",
                "AMMONIA_c",
            }
        )

        # self.add_gpr_annotations(parse_gpr_annotations)
        # self.add_kinetic_data(moped_kinetic_data)
        self.add_monomers(moped_monomers)

        if move_electron_transport_cofactors_to_cytosol:
            self._move_electron_transport_cofactors_to_cytosol()

        if repair_photosynthesis_reactions:
            self._repair_photosynthesis_reactions()

        if fix_periplasm_proton_gradient:
            self._fix_periplasm_proton_gradient()

        if remove_unused_compounds:
            self.remove_unused_compounds()

        if fix_light_reaction_mass_balance:
            self._fix_light_reaction_mass_balance()

    def _read_cobra_annotation(self, annotations: dict[str, str | list[str]]) -> dict[str, set[str]]:
        if "sbo" in annotations:
            annotations.pop("sbo")
        return {k: set(v) if isinstance(v, list) else set([v]) for k, v in annotations.items()}

    def _read_cobra_compounds(
        self,
        cobra_model: cobra.Model,
        compartment_map: dict[str, str],
        compartment_suffixes: re.Pattern,
    ) -> None:
        for metabolite in cobra_model.metabolites:
            base_id = self._strip_compartment_suffix(
                object_id=metabolite.id,
                compartment_pattern=compartment_suffixes,
            )
            compartment = compartment_map[metabolite.compartment]
            database_links = self._read_cobra_annotation(metabolite.annotation)
            self.add_compound(
                Compound(
                    base_id=base_id,
                    compartment=compartment,
                    id=metabolite.id,
                    formula=metabolite.elements,
                    charge=metabolite.charge,
                    name=metabolite.name,
                    gibbs0=None,
                    smiles=None,
                    database_links=database_links,
                    types=list(),
                    in_reaction=set(),
                )
            )

    def _read_cobra_rxn_genes(self, rxn: cobra.Reaction) -> dict[str, Monomer]:
        monomers = {}
        for gene in rxn.genes:
            database_links = self._read_cobra_annotation(gene.annotation)
            gene_id = cast(str, gene.id)
            monomers[gene_id] = Monomer(id=gene_id, sequence=None, database_links=database_links)
        return monomers

    def _read_cobra_rxn_gpr_annotation(self, rxn: cobra.Reaction) -> list[set[str]]:
        return [set(rxn.gene_reaction_rule.split(" and"))]

    def _read_cobra_reactions_and_objective(
        self,
        cobra_model: cobra.Model,
        compartment_map: dict[str, str],
        compartment_suffixes: re.Pattern,
    ) -> None:
        objective = {}
        for reaction in cobra_model.reactions:
            obj_coef = reaction.objective_coefficient
            if obj_coef != 0:
                objective[reaction.id] = obj_coef

            compartment: Union[str, Tuple[str, ...]]
            if len(reaction.compartments) == 1:
                compartment = compartment_map[next(iter(reaction.compartments))]
            else:
                compartment = tuple(compartment_map[i] for i in reaction.compartments)
            database_links = self._read_cobra_annotation(reaction.annotation)
            self.add_monomers(self._read_cobra_rxn_genes(reaction))
            gpr_annotation = self._read_cobra_rxn_gpr_annotation(reaction)
            self.add_reaction(
                Reaction(
                    id=reaction.id,
                    compartment=compartment,
                    stoichiometries={k.id: v for k, v in reaction.metabolites.items()},
                    bounds=reaction.bounds,
                    database_links=database_links,
                    name=reaction.name if len(reaction.name) > 0 else None,
                    base_id=self._strip_compartment_suffix(
                        object_id=reaction.id,
                        compartment_pattern=compartment_suffixes,
                    ),
                    gpr_annotation=gpr_annotation,
                    _gpa=0 if len(gpr_annotation) > 0 else None,
                )
            )
        self.set_objective(objective=objective)

    def read_from_cobra(self, cobra_model: cobra.Model) -> None:
        """Import a cobra model into this model."""
        compartment_map = cobra_model.compartments
        self.compartments.update({v: k for k, v in compartment_map.items()})
        compartment_suffixes = re.compile("|".join(set([f"(_{i}$)" for i in compartment_map.keys()])))
        self._read_cobra_compounds(cobra_model, compartment_map, compartment_suffixes)
        self._read_cobra_reactions_and_objective(cobra_model, compartment_map, compartment_suffixes)

    def read_from_sbml(self, sbml_file: Union[str, Path]) -> None:
        """Import an sbml model into this model."""
        cobra_model = cobra.io.read_sbml_model(filename=str(sbml_file))
        self.read_from_cobra(cobra_model=cobra_model)

    def read_from_bigg(self, bigg_sbml_file: Union[str, Path]) -> None:
        """Import a bigg sbml model into this model."""
        self.read_from_sbml(sbml_file=bigg_sbml_file)

        for strong_cofactor_base_id, weak_cofactor_base_id in {
            "atp": "adp",
            "gtp": "gdp",
            "nadh": "nad",
            "nadph": "nadp",
            "10fthf": "thf",
            "methf": "thf",
            "fdxrd": "fdxox",
            "trdrd": "trdox",
            "etfrd": "etfox",
            "accoa": "coa",
            "pcrd": "pcox",
        }.items():
            self.add_cofactor_pair(
                strong_cofactor_base_id=strong_cofactor_base_id,
                weak_cofactor_base_id=weak_cofactor_base_id,
            )

    ##########################################################################
    # Universal functions
    ##########################################################################

    def create_submodel(self, reaction_ids: Iterable[str], name: str | None = None) -> "Model":
        """Create a subset of the model, containing the given reactions and their compounds."""
        reactions = [self.reactions[i] for i in sorted(reaction_ids)]
        compounds = set()
        for rec in reactions:
            for cpd_name in rec.stoichiometries:
                cpd = copy.deepcopy(self.compounds[cpd_name])
                cpd.in_reaction = set()
                compounds.add(cpd)
        if name is None:
            name = self.name + " submodel"

        submodel = Model(
            compounds=compounds,
            reactions=reactions,
            name=name,
            compartments=self.compartments.copy(),
            objective=self.objective.copy(),
            minimal_seed=self.minimal_seed.copy(),
        )

        # submodel.cofactor_pairs = self.cofactor_pairs.copy()
        # This is wrong, submodel must not necessarily have the same cofactor pairs

        # Collect base cofactor pairs
        base_cofactor_pairs = {}
        for strong, weak in self.cofactor_pairs.items():
            strong_base_cpd = self.compounds[strong].base_id
            weak_base_cpd = self.compounds[weak].base_id
            base_cofactor_pairs[strong_base_cpd] = weak_base_cpd

        # Only add cofactor pairs to submodel that actually exist in there
        for strong, weak in base_cofactor_pairs.items():
            submodel.add_cofactor_pair(
                strong_cofactor_base_id=strong,
                weak_cofactor_base_id=weak,
            )

        # Only export monomers that are actually used
        monomers = {}
        for reaction in self.reactions.values():
            for enzyme in reaction.gpr_annotation:
                for monomer in enzyme:
                    if monomer in self.monomers:
                        monomers[monomer] = self.monomers[monomer]
        submodel.monomers = monomers
        return submodel

    def add_cofactor_pair(self, strong_cofactor_base_id: str, weak_cofactor_base_id: str) -> None:
        """Add a cofactor pair.

        This automatically adds all compartment variants of the given base ids.

        Examples
        --------
        >>> model.add_cofactor_pair("ATP", "ADP")
        """
        try:
            self._base_cofactor_pairs[strong_cofactor_base_id] = weak_cofactor_base_id
            for strong_cpd_id in self.base_compounds[strong_cofactor_base_id]:
                for weak_cpd_id in self.base_compounds[weak_cofactor_base_id]:
                    if self.compounds[strong_cpd_id].compartment == self.compounds[weak_cpd_id].compartment:
                        self.cofactor_pairs[strong_cpd_id] = weak_cpd_id
        except KeyError:
            pass

    def get_weak_cofactors(self) -> List[str]:
        """Get ids of weak cofactors."""
        return list(set([i for i in self.cofactor_pairs.values()]))

    def get_weak_cofactor_duplications(self) -> List[str]:
        """Get ids of weak cofactors including the __cof__ tag.

        This function is useful for structural analyses, in which these
        tagged cofactors are used.
        """
        return list(set([i + "__cof__" for i in self.cofactor_pairs.values()]))

    def get_strong_cofactors(self) -> List[str]:
        """Get ids of strong cofactors."""
        return list(set([i for i in self.cofactor_pairs.keys()]))

    def get_strong_cofactor_duplications(self) -> List[str]:
        """Get ids of strong cofactors including the __cof__ tag.

        This function is useful for structural analyses, in which these
        tagged cofactors are used."""
        return list(set([i + "__cof__" for i in self.cofactor_pairs.keys()]))

    def update_from_reference(
        self, reference_model: "Model", verbose: bool = False
    ) -> Tuple[List[str], Set[str]]:
        """Update a model from a reference Model.

        Returns
        -------
        unmapped_reactions
            Reactions that could not be found in the reference database
        unmapped_compounds
            Compounds that could not be found in the reference database
        """
        mapped_compounds = set(self.compounds).intersection(reference_model.compounds)
        unmapped_compounds = set(self.compounds).difference(reference_model.compounds)

        old_base_reactions = set(self.base_reactions)
        old_variant_reactions = set(self.variant_reactions)

        new_base_reactions = set(reference_model.base_reactions)
        new_variant_reactions = set(reference_model.variant_reactions)

        unmapped_base_reactions = [
            j for i in old_base_reactions.difference(new_base_reactions) for j in self.base_reactions[i]
        ]
        unmapped_variant_reactions = [
            j
            for i in old_variant_reactions.difference(new_variant_reactions)
            for j in self.variant_reactions[i]
        ]
        unmapped_reactions = unmapped_base_reactions + unmapped_variant_reactions

        # Update all existing compounds
        for compound_id in mapped_compounds:
            self.add_compound_from_reference(reference_model=reference_model, compound_id=compound_id)

        # Update all existing base reactions
        for base_reaction_id in old_base_reactions.intersection(
            new_base_reactions
        ) | old_variant_reactions.intersection(new_variant_reactions):
            self.add_reaction_from_reference(
                reference_model=reference_model,
                reaction_id=base_reaction_id,
                update_compounds=True,
            )

        # Updating compounds can change the balance status
        # of the local reactions, thus those that cannot be mapped
        # need to be checked again
        for reaction_id in unmapped_reactions:
            if not self.check_mass_balance(reaction_id=reaction_id):
                self.remove_reaction(reaction_id=reaction_id)
                continue
            if not self.check_charge_balance(reaction_id=reaction_id):
                self.remove_reaction(reaction_id=reaction_id)
        if verbose:
            print(
                f"Could not map {len(unmapped_base_reactions) + len(unmapped_variant_reactions)} reactions "
                + f"and {len(unmapped_compounds)} compounds"
            )
        return unmapped_reactions, unmapped_compounds

    ##########################################################################
    # Compound functions
    ##########################################################################

    def add_compound(self, compound: Compound) -> None:
        """Add a compound to the model. Overwrites existing compounds."""
        if isinstance(compound, Compound):
            if not bool(compound.id):
                compound.id = self._add_compartment_suffix(
                    object_id=compound.base_id,
                    compartment_id=cast(str, compound.compartment),
                )
            cpd_id = cast(str, compound.id)
            self.compounds[cpd_id] = copy.deepcopy(compound)
            self.base_compounds.setdefault(compound.base_id, set()).add(cpd_id)
            for compound_type in compound.types:
                self._compound_types.setdefault(compound_type, set()).add(cpd_id)
        else:
            raise TypeError("Compound has to be of type moped.model.Compound")

    def add_compounds(self, compounds: Iterable[Compound]) -> None:
        """Add multiple compounds to the model. Overwrites existing compounds."""
        for compound in compounds:
            self.add_compound(compound=compound)

    def add_compound_from_reference(self, reference_model: "Model", compound_id: str) -> None:
        """Overwrite local data from reference database or adds new one if it does not exist already."""
        new_cpd = copy.deepcopy(reference_model.compounds[compound_id])
        try:
            old_cpd = self.compounds.pop(compound_id)
            new_cpd.in_reaction = old_cpd.in_reaction
        except KeyError:
            new_cpd.in_reaction = set()
        self.compounds[compound_id] = new_cpd

    def _create_compartment_variant(self, old_compound: Compound, compartment_id: str) -> Compound:
        """Create a variant of the compound in another compartment.

        This empties the in_reaction set, as the compound is only known
        to be part of the reactions in the previous compartment and
        we cannot know whether those reactions are also available
        in the new compartment.
        """
        new_compound = copy.deepcopy(old_compound)
        new_compound.id = self._add_compartment_suffix(
            object_id=old_compound.base_id, compartment_id=compartment_id
        )
        new_compound.compartment = compartment_id
        new_compound.in_reaction = set()
        self.add_compound(compound=new_compound)
        return new_compound

    def add_compartment_compound_variant(self, compound_id: str, compartment_id: str) -> Compound:
        """Add a copy of the compound in the respective compartment."""
        try:
            old_compound = self.compounds[compound_id]
        except KeyError:
            try:
                compound_variants = self.base_compounds[compound_id]
                old_compound = self.compounds[next(iter(compound_variants))]
            except KeyError:
                raise KeyError(f"Compound {compound_id} has to be in the model to create an external variant")
        new_compound_id = self._add_compartment_suffix(
            object_id=old_compound.base_id, compartment_id=compartment_id
        )
        try:
            new_compound = self.compounds[new_compound_id]
        except KeyError:
            new_compound = self._create_compartment_variant(
                old_compound=old_compound, compartment_id=compartment_id
            )
        return new_compound

    def set_compound_property(self, compound_id: str, property_dict: Dict[str, Any]) -> None:
        """Set one or multiple properties of a compound."""
        for k, v in property_dict.items():
            cpd = self.compounds[compound_id]
            slots = dataclasses.asdict(cpd).keys()
            if k not in slots:
                raise KeyError(f"Compound does not have key '{k}', can only be one of {slots}")
            setattr(cpd, k, v)

    def remove_compound(self, compound_id: str) -> None:
        """Remove a compound from the model."""
        compound = self.compounds.pop(compound_id)

        # Also remove from base compounds
        self.base_compounds[compound.base_id].remove(compound_id)
        if not bool(self.base_compounds[compound.base_id]):
            del self.base_compounds[compound.base_id]

        # Also remove from compound types
        for compound_type in compound.types:
            self._compound_types[compound_type].remove(compound_id)
            if not bool(self._compound_types[compound_type]):
                del self._compound_types[compound_type]

        if compound_id in self.cofactor_pairs:
            del self.cofactor_pairs[compound_id]
        elif compound_id in self.get_weak_cofactors():
            weak_cofactors = self.get_weak_cofactors()
            strong_cofactors = self.get_strong_cofactors()
            weak_to_strong = dict(zip(weak_cofactors, strong_cofactors))
            del self.cofactor_pairs[weak_to_strong[compound_id]]

    def remove_compounds(self, compound_ids: Iterable[str]) -> None:
        """Remove multiple compounds from the model."""
        for compound_id in compound_ids:
            self.remove_compound(compound_id=compound_id)

    def remove_unused_compounds(self) -> None:
        """Remove compounds from the model that are in no reaction."""
        all_compounds = set(self.compounds)
        used_compounds = set()
        for reaction in self.reactions.values():
            used_compounds.update(set(reaction.stoichiometries))
        unused = all_compounds.difference(used_compounds)
        self.remove_compounds(compound_ids=unused)

    def get_compound_base_id(self, compound_id: str) -> str:
        """Get the database links of a given compound."""
        return self.compounds[compound_id].base_id

    def get_compound_compartment_variants(self, compound_base_id: str) -> Set[str]:
        """Get compound ids for all respective compartments the compound is in.

        The compound_base_id for ATP_c for example would be ATP.
        """
        return self.base_compounds[compound_base_id]

    def get_compound_compartment(self, compound_id: str) -> str | None:
        """Get compartment of a given compound compound."""
        return self.compounds[compound_id].compartment

    def get_compound_formula(self, compound_id: str) -> Dict[str, float] | None:
        """Get the charge of a given compound."""
        return self.compounds[compound_id].formula

    def get_compound_charge(self, compound_id: str) -> float | None:
        """Get the charge of a given compound."""
        return self.compounds[compound_id].charge

    def get_compound_gibbs0(self, compound_id: str) -> float | None:
        """Get the gibbs energy (free enthalpy) of the given compound."""
        return self.compounds[compound_id].gibbs0

    def get_reactions_of_compound(self, compound_id: str) -> Set[str]:
        """Get all reactions of a compound."""
        return self.compounds[compound_id].in_reaction

    def get_compound_database_links(self, compound_id: str) -> Dict[str, Set[str]]:
        """Get the database links of a given compound."""
        return self.compounds[compound_id].database_links

    def get_base_compound_ids(self) -> Set[str]:
        """Get base IDs of all compounds."""
        return set(i.base_id for i in self.compounds.values())

    def get_compound_type_ids(self) -> Set[str]:
        """Get all available compound types."""
        return set(self._compound_types)

    def get_model_compartment_ids(self) -> Set[str]:
        """Get all ids for compartments used in the model."""
        return set(self.compartments)

    def get_compounds_of_compartment(self, compartment_id: str) -> List[str]:
        """Get all compounds from the respective compartment.

        To look up the available compartments, see model.get_model_compartment_ids

        See Also
        --------
        model.get_model_compartment_ids
            To get all available compartments
        """
        if compartment_id not in self.get_model_compartment_ids():
            raise KeyError(
                f"Unknown compartment {compartment_id}, did you mean any of {self.get_model_compartment_ids()}?"
            )
        return [k for k, v in self.compounds.items() if v.compartment == compartment_id]

    def get_compounds_of_type(self, compound_type: str) -> Set[str]:
        """Get all compound ids of a given compound_type."""
        return self._compound_types[compound_type]

    ##########################################################################
    # Reaction functions
    ##########################################################################

    def add_reaction(self, reaction: Reaction) -> None:
        """Add a reaction to the model."""
        if not isinstance(reaction, Reaction):
            raise TypeError("Reaction has to be of type moped.model.Reaction")
        reaction_id = reaction.id
        if reaction._var is not None:
            self.variant_reactions.setdefault(cast(str, reaction.base_id), set()).add(reaction_id)
        else:
            self.base_reactions.setdefault(cast(str, reaction.base_id), set()).add(reaction_id)
        self.reactions[reaction_id] = copy.deepcopy(reaction)
        for compound in reaction.stoichiometries:
            self.compounds[compound].in_reaction.add(reaction_id)
        for type_ in reaction.types:
            self._reaction_types.setdefault(type_, set()).add(reaction.id)
        for pathway in reaction.pathways:
            self.add_reaction_to_pathway(pathway_id=pathway, reaction_id=reaction_id)

    def add_reactions(self, reactions: Iterable[Reaction]) -> None:
        """Add multiple reactions to the model."""
        for reaction in reactions:
            self.add_reaction(reaction=reaction)

    def add_reaction_from_reference(
        self,
        reference_model: "Model",
        reaction_id: str,
        update_compounds: bool = True,
    ) -> None:
        """Add a reaction from a reference model.

        Always adds reversibiliy and cofactor duplicates as well. In this case all
        existing reaction variants are kept if they are not overwritten.
        Adds all variants of a reaction if the base_id of a variant reaction is given.
        In this case all other existing reaction variants are removed.
        """
        try:
            reaction = self.reactions[reaction_id]
            base_id = cast(str, reaction.base_id)
        except KeyError:
            base_id = reaction_id
        if base_id in reference_model.variant_reactions:
            try:
                for reaction_id in tuple(self.variant_reactions[base_id]):
                    self.remove_reaction(reaction_id)
            except KeyError:
                pass
            new_reactions = [
                reference_model.reactions[reaction_id]
                for reaction_id in reference_model.variant_reactions[base_id]
            ]
            if update_compounds:
                new_compound_ids = {j for i in new_reactions for j in i.stoichiometries}
                for compound_id in new_compound_ids:
                    self.add_compound_from_reference(reference_model=reference_model, compound_id=compound_id)
            for reaction in new_reactions:
                self.add_reaction(reaction=reaction)
                if reaction.id in reference_model._duplicate_reactions:
                    self._duplicate_reactions.add(reaction.id)
        elif base_id in reference_model.base_reactions:
            try:
                for reaction_id in tuple(self.base_reactions[base_id]):
                    self.remove_reaction(reaction_id=reaction_id)
            except KeyError:
                pass
            new_reactions = [
                reference_model.reactions[reaction_id]
                for reaction_id in reference_model.base_reactions[base_id]
            ]
            if update_compounds:
                new_compound_ids = {j for i in new_reactions for j in i.stoichiometries}
                for compound_id in new_compound_ids:
                    self.add_compound_from_reference(reference_model=reference_model, compound_id=compound_id)
            for reaction in new_reactions:
                self.add_reaction(reaction=reaction)
                if reaction.id in reference_model._duplicate_reactions:
                    self._duplicate_reactions.add(reaction.id)
        elif base_id in reference_model.reactions:
            self.add_reaction_from_reference(
                reference_model=reference_model,
                reaction_id=cast(str, reference_model.reactions[reaction_id].base_id),
            )
        else:
            raise KeyError(f"Could not find {reaction_id} in the reference_model")

    def add_reactions_from_reference(
        self,
        reference_model: "Model",
        reaction_ids: Iterable[str],
        update_compounds: bool = True,
    ) -> None:
        """Add reactions from a reference model, overwriting existing reactions."""
        for reaction_id in reaction_ids:
            self.add_reaction_from_reference(
                reference_model=reference_model,
                reaction_id=reaction_id,
                update_compounds=update_compounds,
            )

    def set_reaction_property(self, reaction_id: str, property_dict: Dict[str, Any]) -> None:
        """Set one or multiple properties of a reaction."""
        for k, v in property_dict.items():
            reaction = self.reactions[reaction_id]
            if k in reaction.__dict__:
                setattr(self.reactions[reaction_id], k, v)
            else:
                raise KeyError(f"Reaction does not have key '{k}', can only be one of {Reaction.__dict__}")

    def remove_reaction(self, reaction_id: str, remove_empty_references: bool = True) -> None:
        """Remove a reaction from the model."""
        reaction = self.reactions[reaction_id]
        base_id = cast(str, reaction.base_id)
        if reaction._var is not None:
            self.variant_reactions[base_id].remove(reaction_id)
            if remove_empty_references:
                if not bool(self.variant_reactions[base_id]):
                    del self.variant_reactions[base_id]
        else:
            self.base_reactions[base_id].remove(reaction_id)
            if remove_empty_references:
                if not bool(self.base_reactions[base_id]):
                    del self.base_reactions[base_id]
        for pathway in tuple(reaction.pathways):
            self.remove_reaction_from_pathway(pathway_id=pathway, reaction_id=reaction_id)
        for compound in reaction.stoichiometries:
            self.compounds[compound].in_reaction.remove(reaction_id)
            if remove_empty_references:
                if not bool(self.compounds[compound].in_reaction):
                    del self.compounds[compound]
        for type_ in reaction.types:
            self._reaction_types[type_].remove(reaction_id)
            if remove_empty_references:
                if not bool(self._reaction_types[type_]):
                    del self._reaction_types[type_]
        del self.reactions[reaction_id]

    def remove_reactions(self, reaction_ids: Iterable[str]) -> None:
        """Remove multiple reactions from the model."""
        for reaction_id in reaction_ids:
            self.remove_reaction(reaction_id=reaction_id)

    def get_reaction_base_id(self, reaction_id: str) -> str | None:
        """Get the base id of a given reaction."""
        return self.reactions[reaction_id].base_id

    def get_reaction_compartment_variants(self, reaction_base_id: str) -> Set[str]:
        """Get the ids of the reaction in all compartments it takes place in."""
        return self.base_reactions[reaction_base_id]

    def get_reaction_compartment(self, reaction_id: str) -> str | Tuple[str, ...] | None:
        """Get the compartment of a given reaction."""
        return self.reactions[reaction_id].compartment

    def get_reaction_gibbs0(self, reaction_id: str) -> float | None:
        """Get the database links of a given reaction."""
        return self.reactions[reaction_id].gibbs0

    def get_reaction_bounds(self, reaction_id: str) -> Tuple[float, float] | None:
        """Get the bounds of a given reaction."""
        return self.reactions[reaction_id].bounds

    def get_reaction_reversibility(self, reaction_id: str) -> bool | None:
        """Get whether a reaction is reversible."""
        return self.reactions[reaction_id].reversible

    def get_reaction_pathways(self, reaction_id: str) -> Set[str]:
        """Get the pathways of a given reaction."""
        return self.reactions[reaction_id].pathways

    def get_reaction_sequences(self, reaction_id: str) -> Dict[str, str]:
        """Get the protein sequences of a given reaction."""
        sequences = {}
        reaction = self.reactions[reaction_id]
        for enzyme in reaction.gpr_annotation:
            for mon_id in enzyme:
                if (mon := self.monomers.get(mon_id)) is not None:
                    if (seq := mon.sequence) is not None:
                        sequences[mon_id] = seq
        return sequences

    def get_reaction_types(self, reaction_id: str) -> List[str]:
        """Get the types of a given reaction."""
        return self.reactions[reaction_id].types

    def get_reaction_database_links(self, reaction_id: str) -> Dict[str, Set[str]]:
        """Get the database links of a given reaction."""
        return self.reactions[reaction_id].database_links

    def get_base_reaction_ids(self) -> Set[str]:
        """Get base IDs of all reactions."""
        return set(self.base_reactions)

    def get_reaction_type_ids(self) -> Set[str]:
        """Get all available reaction types."""
        return set(self._reaction_types)

    def get_reactions_of_type(self, reaction_type: str) -> Set[str]:
        """Get all reaction ids of a given type."""
        return self._reaction_types[reaction_type]

    def get_reaction_variants(self, base_reaction_id: str) -> Set[str]:
        """Get all reaction variants."""
        return self.variant_reactions[base_reaction_id]

    def get_reversible_reactions(self) -> List[str]:
        """Get all reactions marked as reversible."""
        return [k for k, v in self.reactions.items() if v.reversible]

    def get_irreversible_reactions(self) -> List[str]:
        """Get all reactions marked as irreversible."""
        return [k for k, v in self.reactions.items() if not v.reversible]

    def get_transmembrane_reactions(self) -> List[str]:
        """Get reaction ids for reactions with compounds in two compartments."""
        return [k for k, v in self.reactions.items() if v.transmembrane]

    def get_reactions_of_compartment(
        self, compartment_id: str, include_transporters: bool = True
    ) -> Set[str]:
        """Reaction reaction ids for reactions that occur in a given compartment."""
        reaction_ids = {
            reaction_id
            for compound_id in self.get_compounds_of_compartment(compartment_id=compartment_id)
            for reaction_id in self.compounds[compound_id].in_reaction
        }
        if include_transporters:
            return reaction_ids
        return reaction_ids.difference(self.get_transmembrane_reactions())

    def get_transport_reactions(self, compartment_id: str) -> Set[str]:
        """Get reactions that transport something in/out of a given compartment."""
        compartment_reactions = self.get_reactions_of_compartment(
            compartment_id=compartment_id, include_transporters=True
        )
        transmembrane_reactions = self.get_transmembrane_reactions()
        return set(transmembrane_reactions).intersection(compartment_reactions)

    ##########################################################################
    # Pathway functions
    ##########################################################################

    def add_pathway(self, pathway_id: str, pathway_reactions: Iterable[str]) -> None:
        """Add a pathway to the model."""
        for reaction_id in pathway_reactions:
            self.reactions[reaction_id].pathways.add(pathway_id)
        self.pathways.setdefault(pathway_id, set()).update(pathway_reactions)

    def add_reaction_to_pathway(self, pathway_id: str, reaction_id: str) -> None:
        """Add a reaction to a pathway."""
        self.reactions[reaction_id].pathways.add(pathway_id)
        self.pathways.setdefault(pathway_id, set()).add(reaction_id)

    def remove_pathway(self, pathway_id: str) -> None:
        """Remove a pathway from the model."""
        reactions = self.pathways.pop(pathway_id)
        for reaction in reactions:
            self.reactions[reaction].pathways.remove(pathway_id)

    def remove_reaction_from_pathway(self, pathway_id: str, reaction_id: str) -> None:
        """Remove a reaction from a pathway."""
        self.pathways[pathway_id].remove(reaction_id)
        self.reactions[reaction_id].pathways.remove(pathway_id)
        # Remove pathway completely if it is empty
        if self.pathways[pathway_id] == set():
            self.remove_pathway(pathway_id=pathway_id)

    def get_reactions_of_pathway(self, pathway_id: str) -> Set[str]:
        """Get all reactions that are part of a pathway."""
        return self.pathways[pathway_id]

    def get_pathway_ids(self) -> list[str]:
        """Get all pathway ids."""
        return list(self.pathways.keys())

    ##########################################################################
    # Medium, biomass and objective functions
    ##########################################################################

    def add_transport_reaction(
        self,
        compound_id: str,
        compartment_id: str,
        bounds: Tuple[float, float] = (-1000, 1000),
    ) -> None:
        """Add a transport reaction into another compartment."""
        orig_compartment = self.compounds[compound_id].compartment
        into_cpd = self.add_compartment_compound_variant(
            compound_id=compound_id, compartment_id=compartment_id
        )
        into_suffix = self._add_compartment_suffix(object_id="", compartment_id=compartment_id)
        self.add_reaction(
            Reaction(
                id=f"TR_{compound_id}{into_suffix}",
                base_id=f"TR_{compound_id}",
                stoichiometries={compound_id: -1, cast(str, into_cpd.id): 1},
                bounds=bounds,
                transmembrane=True,
                compartment=(orig_compartment, compartment_id),
            )
        )

    def add_influx(self, compound_id: str, extracellular_compartment_id: str) -> None:
        """Add an influx of a compound to the model."""
        # Add influx
        orig_compartment = self.compounds[compound_id].compartment
        ex_met = self.add_compartment_compound_variant(
            compound_id=compound_id, compartment_id=extracellular_compartment_id
        )
        self.add_reaction(
            Reaction(
                id=f"EX_{ex_met.base_id}_e",
                base_id=f"EX_{ex_met.base_id}",
                stoichiometries={cast(str, ex_met.id): -1},
                bounds=(-1000, 0),
                compartment=(orig_compartment, extracellular_compartment_id),
            )
        )

    def remove_influx(self, compound_id: str) -> None:
        """Remove the influx of a given compound."""
        try:
            compound = self.compounds[compound_id]
            base_compound_id = compound.base_id
        except KeyError:
            if compound_id not in self.base_compounds:
                raise KeyError(f"Compound {compound_id} neither found in compounds nor base compounds")
            base_compound_id = compound_id
        self.remove_reaction(reaction_id=f"EX_{base_compound_id}_e")

    def add_efflux(self, compound_id: str, extracellular_compartment_id: str) -> None:
        """Add an efflux of a compound to the model."""
        # Add efflux
        orig_compartment = self.compounds[compound_id].compartment
        ex_met = self.add_compartment_compound_variant(
            compound_id=compound_id, compartment_id=extracellular_compartment_id
        )
        self.add_reaction(
            Reaction(
                id=f"EX_{ex_met.base_id}_e",
                base_id=f"EX_{ex_met.base_id}",
                stoichiometries={cast(str, ex_met.id): -1},
                bounds=(0, 1000),
                compartment=(orig_compartment, extracellular_compartment_id),
            )
        )

    def remove_efflux(self, compound_id: str) -> None:
        """Remove the efflux of a given compound."""
        try:
            compound = self.compounds[compound_id]
            base_compound_id = compound.base_id
        except KeyError:
            if compound_id not in self.base_compounds:
                raise KeyError(f"Compound {compound_id} neither found in compounds nor base compounds")
            base_compound_id = compound_id
        self.remove_reaction(reaction_id=f"EX_{base_compound_id}_e")

    def add_medium_component(self, compound_id: str, extracellular_compartment_id: str) -> None:
        """Add a compound as a medium component."""
        # Add medium influx/efflux
        orig_compartment = self.compounds[compound_id].compartment
        ex_met = self.add_compartment_compound_variant(
            compound_id=compound_id, compartment_id=extracellular_compartment_id
        )
        self.add_reaction(
            Reaction(
                id=f"EX_{ex_met.base_id}_e",
                base_id=f"EX_{ex_met.base_id}",
                stoichiometries={cast(str, ex_met.id): -1},
                bounds=(-1000, 1000),
                compartment=(orig_compartment, extracellular_compartment_id),
            )
        )

    def remove_medium_component(self, compound_id: str) -> None:
        """Remove influx and outflux of a given compound."""
        try:
            compound = self.compounds[compound_id]
            base_compound_id = compound.base_id
        except KeyError:
            if compound_id not in self.base_compounds:
                raise KeyError(f"Compound {compound_id} neither found in compounds nor base compounds")
            base_compound_id = compound_id
        self.remove_reaction(reaction_id=f"EX_{base_compound_id}_e")

    def get_biomass_template(self, organism: str = "ecoli") -> Dict[str, float]:
        """Return an organism specific biomass composition."""
        try:
            return BIOMASS_TEMPLATES[organism]
        except KeyError:
            raise KeyError(
                f"Could not find template for organism {organism}. "
                + f"Currenly supported organisms are {tuple(BIOMASS_TEMPLATES)}"
            )

    def set_objective(self, objective: Dict[str, float]) -> None:
        """Set the objective function(s)."""
        for reaction_id in objective:
            if reaction_id not in self.reactions:
                raise KeyError(f"Objective reaction {reaction_id} is not in the model")
        self.objective = dict(objective)

    ##########################################################################
    # Quality control interface
    ##########################################################################

    def check_charge_balance(self, reaction_id: str, verbose: bool = False) -> bool:
        """Check the charge balance of a reaction."""
        substrate_charge = 0.0
        product_charge = 0.0
        for k, v in self.reactions[reaction_id].stoichiometries.items():
            charge = self.compounds[k].charge
            if charge is None:
                return False
            if v < 0:
                substrate_charge -= charge * v
            else:
                product_charge += charge * v
        if verbose:
            print(f"Substrate charge: {substrate_charge}")
            print(f"Product charge: {product_charge}")
        if substrate_charge - product_charge == 0:
            return True
        return False

    def check_mass_balance(self, reaction_id: str, verbose: bool = False) -> bool:
        """Check the mass balance of a reaction."""
        lhs_atoms: DefaultDict[str, float] = defaultdict(int)
        rhs_atoms: DefaultDict[str, float] = defaultdict(int)
        for k, v in self.reactions[reaction_id].stoichiometries.items():
            formula = self.compounds[k].formula
            if not bool(formula):
                return False
            if v < 0:
                for atom, stoich in formula.items():
                    lhs_atoms[atom] -= stoich * v
            else:
                for atom, stoich in formula.items():
                    rhs_atoms[atom] += stoich * v
        if verbose:
            print(dict(lhs_atoms))
            print(dict(rhs_atoms))
        for k in set((*lhs_atoms, *rhs_atoms)):
            diff = lhs_atoms[k] - rhs_atoms[k]
            if diff != 0:
                return False
        return True

    ###########################################################################
    # Stoichiometric functions
    ###########################################################################

    def get_stoichiometric_matrix(self) -> np.ndarray:
        """Return the stoichiometric matrix."""
        cpd_mapper = dict(zip(self.compounds, range(len(self.compounds))))
        N = np.zeros((len(self.compounds), len(self.reactions)))
        for i, rxn in enumerate(self.reactions.values()):
            for cpd, val in rxn.stoichiometries.items():
                N[cpd_mapper[cpd], i] = val
        return N

    def get_stoichiometric_df(self) -> pd.DataFrame:
        """Return the stoichiometric matrix as an annotated pandas dataframe."""
        return pd.DataFrame(
            self.get_stoichiometric_matrix(),
            index=cast(list, self.compounds),  # actually keys(), but doesn't matter
            columns=cast(list, self.reactions),  # actually keys(), but doesn't matter
        )

    ##########################################################################
    # Structural functions
    ##########################################################################

    def add_minimal_seed(self, compound_ids: Iterable[str]) -> None:
        """Add compounds that make up a minimal seed for the given organism."""
        for compound in compound_ids:
            self.minimal_seed.add(compound)

    def get_minimal_seed(self, carbon_source_id: str) -> Set[str]:
        """Get a minimal seed for most organisms."""
        if not bool(self.minimal_seed):
            raise ValueError(
                "No minimal seed defined for this database. You can define one with Model.add_minimal_seed"
            )
        seed = self.minimal_seed.copy()
        seed.add(carbon_source_id)
        return seed

    def reversibility_duplication(self) -> None:
        """Add additional reverse reactions for all reactions that are reversible.

        Useful for structural analyses as scope and gapfilling

        Adds the __rev__ tag to those reactions.
        """
        for reaction_id in self.get_reversible_reactions():
            rev_reaction = copy.deepcopy(self.reactions[reaction_id])
            rev_reaction.id += "__rev__"
            rev_reaction.reverse_stoichiometry()
            self.add_reaction(reaction=rev_reaction)
            self._duplicate_reactions.add(rev_reaction.id)

    def remove_reversibility_duplication(self) -> None:
        """Remove the additional reverse reactions introduced.

        by model.reversibility_duplication
        """
        for reaction_id in tuple(self._duplicate_reactions):
            if "__rev__" in reaction_id:
                self.remove_reaction(reaction_id=reaction_id)
                self._duplicate_reactions.remove(reaction_id)
        self._duplicate_reactions = set()

    def cofactor_duplication(self) -> None:
        """Add additional reactions for reactions carrying cofactor pairs.

        Adds a __cof__ tag for every reaction that contains one of the cofactor pairs in model.cofactor_pairs.

        Useful for structural analyses as scope and gapfilling
        """
        # Add all cofacor metabolites, if they are in the model
        for k, v in self.cofactor_pairs.items():
            if k in self.compounds:
                cof_cpd = copy.deepcopy(self.compounds[k])
                cof_cpd.id = cast(str, cof_cpd.id) + "__cof__"
                cof_cpd.in_reaction = set()
                self.add_compound(compound=cof_cpd)

                pair_cpd = copy.deepcopy(self.compounds[v])
                pair_cpd.id = cast(str, pair_cpd.id) + "__cof__"
                pair_cpd.in_reaction = set()
                self.add_compound(compound=pair_cpd)

        for reaction in tuple(self.reactions.values()):
            reaction_cofactors = []
            for cof, pair in self.cofactor_pairs.items():
                if cof in reaction.stoichiometries:
                    if pair in reaction.stoichiometries:
                        if reaction.stoichiometries[cof] == -reaction.stoichiometries[pair]:
                            reaction_cofactors.append((cof, pair))
            if len(reaction_cofactors) > 0:
                cofactor_reaction = copy.deepcopy(self.reactions[reaction.id])
                cofactor_reaction.id += "__cof__"
                for (cof, pair) in reaction_cofactors:
                    cofactor_reaction.replace_compound(old_compound=cof, new_compound=cof + "__cof__")
                    cofactor_reaction.replace_compound(old_compound=pair, new_compound=pair + "__cof__")
                self.add_reaction(reaction=cofactor_reaction)
                self._duplicate_reactions.add(cofactor_reaction.id)

    def remove_cofactor_duplication(self) -> None:
        """Remove the additional reverse reactions introduced by model.cofactor_duplication."""
        for reaction_id in tuple(self._duplicate_reactions):
            if "__cof__" in reaction_id:
                self.remove_reaction(reaction_id)
                self._duplicate_reactions.remove(reaction_id)

    def breadth_first_search(
        self,
        start_compound_id: str,
        end_compound_id: str,
        max_iterations: int = 50,
        ignored_reaction_ids: Iterable[str] | None = None,
        ignored_compound_ids: Iterable[str] | None = None,
    ) -> SearchResult:
        """Breadth-first search to find shortest path connecting two metabolites."""
        metabolites, reactions = topological.metabolite_tree_search(
            model=self,
            start_compound_id=start_compound_id,
            end_compound_id=end_compound_id,
            max_iterations=max_iterations,
            ignored_reaction_ids=ignored_reaction_ids,
            ignored_compound_ids=ignored_compound_ids,
            search_type="breadth-first",
        )
        return SearchResult(reactions=reactions, compounds=metabolites)

    def depth_first_search(
        self,
        start_compound_id: str,
        end_compound_id: str,
        max_iterations: int = 50,
        ignored_reaction_ids: Iterable[str] | None = None,
        ignored_compound_ids: Iterable[str] | None = None,
    ) -> SearchResult:
        """Depth-first search to find shortest path connecting two metabolites.

        Parameters
        ----------
        start_compound_id: str
        end_compound_id: str
        max_iterations: int
        ignored_reaction_ids: iterable(str)
        ignored_compound_ids: iterable(str)

        Returns
        -------
        metabolites: list(str)
        reactions: list(str)"""
        metabolites, reactions = topological.metabolite_tree_search(
            model=self,
            start_compound_id=start_compound_id,
            end_compound_id=end_compound_id,
            max_iterations=max_iterations,
            ignored_reaction_ids=ignored_reaction_ids,
            ignored_compound_ids=ignored_compound_ids,
            search_type="depth-first",
        )
        return SearchResult(reactions=reactions, compounds=metabolites)

    def scope(
        self,
        seed: Iterable[str],
        include_weak_cofactors: bool = False,
        return_lumped_results: bool = True,
    ) -> Tuple[Set[str], Set[str]] | Tuple[list[Set[str]], list[Set[str]]]:
        """Run the scope algorithm for a single seed.

        Returns
        -------
        scope_reactions
            Can be turned into a list of sets for the respective iteration with
            return_lumped_results=False
        scope_compounds
            Can be turned into a list of sets for the respective iteration with
            return_lumped_results=False


        See Also
        --------
        model.multiple_scopes
        """
        return topological.scope(
            model=self,
            seed=seed,
            include_weak_cofactors=include_weak_cofactors,
            return_lumped_results=return_lumped_results,
        )

    def multiple_scopes(
        self,
        seeds: Iterable[Iterable[str]],
        include_weak_cofactors: bool = False,
        return_lumped_results: bool = True,
        multiprocessing: bool = False,
    ) -> Dict[tuple, Tuple[Set[str], Set[str]] | Tuple[list[Set[str]], list[Set[str]]]]:
        """Run the scope algorithm for multiple seeds.

        Returns
        -------
        scope_reactions
            Can be turned into a list of sets for the respective iteration with
            return_lumped_results=False
        scope_compounds
            Can be turned into a list of sets for the respective iteration with
            return_lumped_results=False


        See Also
        --------
        model.scope
        """
        return topological.multiple_scopes(
            model=self,
            seeds=seeds,
            include_weak_cofactors=include_weak_cofactors,
            return_lumped_results=return_lumped_results,
            multiprocessing=multiprocessing,
        )

    def get_gapfilling_reactions(
        self,
        reference_model: "Model",
        seed: Iterable[str],
        targets: Iterable[str],
        include_weak_cofactors: bool = False,
        verbose: bool = False,
    ) -> List[str]:
        """Find reactions out of a reference model necessary to produce
        all given targets from a given seed"""
        return topological.gapfilling(
            model=self,
            reference_model=reference_model,
            seed=seed,
            targets=targets,
            include_weak_cofactors=include_weak_cofactors,
            verbose=verbose,
        )

    def gapfilling(
        self,
        reference_model: "Model",
        seed: Iterable[str],
        targets: Iterable[str],
        include_weak_cofactors: bool = False,
        verbose: bool = False,
    ) -> None:
        """Run the gapfilling algorithm and add the results to the model."""
        gapfilling_reactions = self.get_gapfilling_reactions(
            reference_model=reference_model,
            seed=seed,
            targets=targets,
            include_weak_cofactors=include_weak_cofactors,
            verbose=verbose,
        )
        if verbose:
            print(f"Adding reactions {gapfilling_reactions}")
        self.add_reactions_from_reference(
            reference_model=reference_model,
            reaction_ids=gapfilling_reactions,
            update_compounds=True,
        )

    ##########################################################################
    # Export functions
    ##########################################################################

    def to_cobra(self) -> cobra.Model:
        """Export the model into a cobra model to do FBA topological."""
        model = cobra.Model(self.name)
        model.compartments = {v: k for k, v in self.compartments.items()}
        model.add_metabolites(
            [
                cobra.Metabolite(
                    id=cpd.id,
                    formula=cpd.formula_to_string(),
                    charge=cpd.charge,
                    compartment=self.compartments[cast(str, cpd.compartment)],
                )
                for cpd in self.compounds.values()
            ]
        )

        for rxn in self.reactions.values():
            c_rxn = cobra.Reaction(id=rxn.id)
            model.add_reaction(c_rxn)
            c_rxn.bounds = rxn.bounds if rxn.bounds else (0, 1000)
            c_rxn.add_metabolites(rxn.stoichiometries)

        if self.objective is not None:
            model.objective = {model.reactions.get_by_id(k): v for k, v in self.objective.items()}
        return model

    ##########################################################################
    # Cobra interface
    ##########################################################################

    def get_influx_reactions(
        self,
        cobra_solution: cobra.Solution | pd.Series,
        sort_result: bool = False,
    ) -> pd.DataFrame:
        """Get influxes from a cobra simulation."""
        exchange_reactions = {i for i in self.reactions if i.startswith("EX_")}
        exchange_fluxes = cobra_solution[exchange_reactions]  # type: ignore
        result = exchange_fluxes[exchange_fluxes > 0]
        if sort_result:
            return result.sort_values(ascending=False)
        return result

    def get_efflux_reactions(
        self,
        cobra_solution: cobra.Solution | pd.Series,
        sort_result: bool = False,
    ) -> pd.DataFrame:
        """Get effluxes from a cobra simulation."""
        exchange_reactions = {i for i in self.reactions if i.startswith("EX_")}
        exchange_fluxes = cobra_solution[exchange_reactions]  # type: ignore
        result = exchange_fluxes[exchange_fluxes < 0]
        if sort_result:
            return result.sort_values(ascending=True)
        return result

    def get_producing_reactions(
        self,
        cobra_solution: cobra.Solution | pd.Series,
        compound_id: str,
        cutoff: float = 0,
    ) -> dict[str, float]:
        """Get reactions that produce the compound in the cobra simulation."""
        producing = {}
        for reaction_id in self.compounds[compound_id].in_reaction:
            flux = cobra_solution[reaction_id] * self.reactions[reaction_id].stoichiometries[compound_id]
            if flux > cutoff:
                producing[reaction_id] = flux
        return producing

    def get_consuming_reactions(
        self,
        cobra_solution: cobra.Solution | pd.Series,
        compound_id: str,
        cutoff: float = 0,
    ) -> dict[str, float]:
        """Get reactions that consume the compound in the cobra simulation."""
        consuming = {}
        for reaction_id in self.compounds[compound_id].in_reaction:
            flux = -cobra_solution[reaction_id] * self.reactions[reaction_id].stoichiometries[compound_id]
            if flux > cutoff:
                consuming[reaction_id] = flux
        return consuming

    ##########################################################################
    # modelbase interface
    ##########################################################################

    @staticmethod
    def _add_modelbase_influx_reaction(
        mod: ode.Model,
        rxn_id: str,
        metabolite: List[str],
        ratelaw: str = "constant",
        suffix: str | None = None,
    ) -> None:
        if ratelaw == "constant":
            k_in = f"k_in_{rxn_id}"
            mod.add_parameters({k_in: 1})
            if suffix is not None:
                rxn_id += f"_{suffix}"
            mod.add_reaction_from_ratelaw(
                rate_name=rxn_id,
                ratelaw=rl.Constant(product=metabolite[0], k=k_in),
            )
        else:
            raise NotImplementedError

    @staticmethod
    def _add_modelbase_efflux_reaction(
        mod: ode.Model,
        rxn_id: str,
        metabolite: List[str],
        ratelaw: str = "mass-action",
        suffix: str | None = None,
    ) -> None:
        if ratelaw == "mass-action":
            k_out = f"k_out_{rxn_id}"
            mod.add_parameters({k_out: 1})
            if suffix is not None:
                rxn_id += f"_{suffix}"
            mod.add_reaction_from_ratelaw(
                rate_name=rxn_id,
                ratelaw=rl.MassAction(substrates=metabolite, products=[], k_fwd=k_out),
            )
        else:
            raise NotImplementedError

    def _add_modelbase_medium_reaction(
        self,
        mod: ode.Model,
        rxn_id: str,
        metabolite: List[str],
        influx_ratelaw: str = "constant",
        efflux_ratelaw: str = "mass-action",
    ) -> None:
        self._add_modelbase_influx_reaction(
            mod=mod,
            rxn_id=rxn_id,
            metabolite=metabolite,
            ratelaw=influx_ratelaw,
            suffix="in",
        )
        self._add_modelbase_efflux_reaction(
            mod=mod,
            rxn_id=rxn_id,
            metabolite=metabolite,
            ratelaw=efflux_ratelaw,
            suffix="out",
        )

    @staticmethod
    def _add_modelbase_irreversible_reaction(
        mod: ode.Model,
        rxn_id: str,
        substrates: List[str],
        products: List[str],
        ratelaw: str = "mass-action",
    ) -> None:
        if ratelaw == "mass-action":
            k_fwd = f"k_{rxn_id}"
            mod.add_parameters({k_fwd: 1})
            mod.add_reaction_from_ratelaw(
                rate_name=rxn_id,
                ratelaw=rl.MassAction(substrates=substrates, products=products, k_fwd=k_fwd),
            )
        else:
            raise NotImplementedError

    @staticmethod
    def _add_modelbase_reversible_reaction(
        mod: ode.Model,
        rxn_id: str,
        substrates: List[str],
        products: List[str],
        ratelaw: str = "mass-action",
    ) -> None:
        if ratelaw == "mass-action":
            k_fwd = f"kf_{rxn_id}"
            k_bwd = f"kr_{rxn_id}"
            mod.add_parameters({k_fwd: 1, k_bwd: 1})
            mod.add_reaction_from_ratelaw(
                rate_name=rxn_id,
                ratelaw=rl.ReversibleMassAction(
                    substrates=substrates,
                    products=products,
                    k_fwd=k_fwd,
                    k_bwd=k_bwd,
                ),
            )
        else:
            raise NotImplementedError

    @staticmethod
    def _stoich_dict_to_list(stoich_dict: Dict[str, float], reaction: str) -> List[str]:
        stoich_list = []
        for cpd, stoich in stoich_dict.items():
            if not stoich == int(stoich):
                warnings.warn(f"Check stoichiometries for reaction {reaction}, possible integer rounddown.")
            stoich_list.extend([cpd] * max(int(abs(stoich)), 1))
        return stoich_list

    def to_kinetic_model(
        self,
        reaction_ratelaw: str = "mass-action",
        influx_ratelaw: str = "constant",
        efflux_ratelaw: str = "mass-action",
    ) -> ode.Model:
        """Convert the model into a kinetic modelbase model."""
        mod = ode.Model()
        mod.add_compounds(sorted(self.compounds))

        for rxn_id, reaction in sorted(self.reactions.items()):
            _substrates, _products = reaction.split_stoichiometries()
            substrates = self._stoich_dict_to_list(_substrates, reaction=rxn_id)
            products = self._stoich_dict_to_list(_products, reaction=rxn_id)

            if len(reaction.stoichiometries) == 1:
                if reaction.reversible:
                    self._add_modelbase_medium_reaction(
                        mod=mod,
                        rxn_id=rxn_id,
                        metabolite=substrates,
                        influx_ratelaw=influx_ratelaw,
                        efflux_ratelaw=efflux_ratelaw,
                    )
                else:
                    if reaction.bounds is not None and reaction.bounds[0] < 0:
                        self._add_modelbase_influx_reaction(
                            mod=mod,
                            rxn_id=rxn_id,
                            metabolite=substrates,
                            ratelaw=influx_ratelaw,
                        )
                    else:
                        self._add_modelbase_efflux_reaction(
                            mod=mod,
                            rxn_id=rxn_id,
                            metabolite=substrates,
                            ratelaw=efflux_ratelaw,
                        )
            else:
                if reaction.reversible:
                    self._add_modelbase_reversible_reaction(
                        mod=mod,
                        rxn_id=rxn_id,
                        substrates=substrates,
                        products=products,
                        ratelaw=reaction_ratelaw,
                    )
                else:
                    self._add_modelbase_irreversible_reaction(
                        mod=mod,
                        rxn_id=rxn_id,
                        substrates=substrates,
                        products=products,
                        ratelaw=reaction_ratelaw,
                    )
        return mod

    def to_kinetic_model_source_code(
        self,
        reaction_ratelaw: str = "mass-action",
        influx_ratelaw: str = "constant",
        efflux_ratelaw: str = "mass-action",
    ) -> str:
        """Convert the model into modelbase model soure code."""
        mod = self.to_kinetic_model(
            reaction_ratelaw=reaction_ratelaw,
            influx_ratelaw=influx_ratelaw,
            efflux_ratelaw=efflux_ratelaw,
        )
        return mod.generate_model_source_code()  # type: ignore

    ##########################################################################
    # Blast interface
    ##########################################################################

    def get_monomer_sequences(self, reaction_ids: Iterable[str]) -> Set[str]:
        """Get monomer sequences from the given reaction_ids."""
        sequences = set()
        for reaction_id in reaction_ids:
            for name, sequence in self.get_reaction_sequences(reaction_id).items():
                sequences.add(f">gnl|META|{name}\n{sequence}")
        return sequences

    def get_all_monomer_sequences(self) -> Set[str]:
        """Get monomer sequences of all reactions."""
        return self.get_monomer_sequences(self.reactions.keys())

    def blast_sequences_against_genome(
        self, sequences: Iterable[str], genome_file: str | Path
    ) -> pd.DataFrame:
        genome_file = Path(genome_file)
        if not genome_file.is_file():
            raise FileNotFoundError(f"genome_file '{genome_file}' does not exist.")
        return topological.tblastn_pipeline(sequences=sequences, genome_file=genome_file)

    def blast_sequences_against_proteome(
        self, sequences: Iterable[str], proteome_file: str | Path
    ) -> pd.DataFrame:
        proteome_file = Path(proteome_file)
        if not proteome_file.is_file():
            raise FileNotFoundError(f"proteome_file '{proteome_file}' does not exist.")
        return topological.blastp_pipeline(sequences=sequences, proteome_file=proteome_file)

    def blast_reactions_against_genome(
        self, reaction_ids: Iterable[str], genome_file: str | Path
    ) -> pd.DataFrame:
        sequences = self.get_monomer_sequences(reaction_ids=reaction_ids)
        return self.blast_sequences_against_genome(sequences=sequences, genome_file=genome_file)

    def blast_reactions_against_proteome(
        self, reaction_ids: Iterable[str], proteome_file: str | Path
    ) -> pd.DataFrame:
        sequences = self.get_monomer_sequences(reaction_ids=reaction_ids)
        return self.blast_sequences_against_proteome(sequences=sequences, proteome_file=proteome_file)

    def blast_all_reactions_against_genome(self, genome_file: str | Path) -> pd.DataFrame:
        sequences = self.get_all_monomer_sequences()
        return self.blast_sequences_against_genome(sequences=sequences, genome_file=genome_file)

    def blast_all_reactions_against_proteome(self, proteome_file: str | Path) -> pd.DataFrame:
        sequences = self.get_all_monomer_sequences()
        return self.blast_sequences_against_proteome(sequences=sequences, proteome_file=proteome_file)

    ##########################################################################
    # Build submodels from blast results
    ##########################################################################

    def create_submodel_from_blast_monomers(
        self,
        blast_monomers: pd.DataFrame,
        name: str | None = None,
        max_evalue: float = 1e-6,
        min_coverage: float = 85,
        min_pident: float = 85,
        prefix_remove: str = r"gnl\|.*?\|",
        suffix_remove: str | None = None,
    ) -> "Model":
        """Create a submodel from given blast results."""
        filtered_blast_monomers = topological.filter_blast_results(
            blast_monomers=blast_monomers,
            max_evalue=max_evalue,
            min_coverage=min_coverage,
            min_pident=min_pident,
            prefix_remove=prefix_remove,
            suffix_remove=suffix_remove,
        )
        blast_reactions: Dict[str, int] = dict()
        for reaction in self.reactions.values():
            for i, monomers in enumerate(reaction.gpr_annotation):
                if monomers.issubset(filtered_blast_monomers):
                    blast_reactions[reaction.id] = i
                    break
        submodel = self.create_submodel(reaction_ids=blast_reactions, name=name)
        for rxn_id, enzrxn in blast_reactions.items():
            submodel.reactions[rxn_id]._gpa = enzrxn
        return submodel

    def create_submodel_from_sequences_and_genome(
        self,
        sequences: Iterable[str],
        genome_file: str | Path,
        name: str | None = None,
        max_evalue: float = 1e-6,
        min_coverage: float = 85,
        min_pident: float = 85,
        prefix_remove: str = r"gnl\|.*?\|",
        suffix_remove: str = None,
        cache_blast_results: bool = False,
    ) -> "Model":
        if cache_blast_results:
            if name is None:
                raise ValueError("Name has to be given in order to cache results")
            blast_file = get_temporary_directory(subdirectory="blast") / f"blast_genome_monomers_{name}.csv"
            if blast_file.is_file():
                blast_monomers = pd.read_csv(blast_file, index_col=0)
            else:
                print(f"Caching results to {blast_file}")
                blast_monomers = self.blast_sequences_against_genome(
                    sequences=sequences, genome_file=genome_file
                )
                blast_monomers.to_csv(blast_file)
        else:
            blast_monomers = self.blast_sequences_against_genome(sequences=sequences, genome_file=genome_file)
        return self.create_submodel_from_blast_monomers(
            blast_monomers=blast_monomers,
            name=name,
            max_evalue=max_evalue,
            min_coverage=min_coverage,
            min_pident=min_pident,
            prefix_remove=prefix_remove,
            suffix_remove=suffix_remove,
        )

    def create_submodel_from_genome(
        self,
        genome_file: str | Path,
        name: str | None = None,
        max_evalue: float = 1e-6,
        min_coverage: float = 85,
        min_pident: float = 85,
        prefix_remove: str = r"gnl\|.*?\|",
        suffix_remove: str = None,
        cache_blast_results: bool = False,
    ) -> "Model":
        return self.create_submodel_from_sequences_and_genome(
            self.get_all_monomer_sequences(),
            genome_file=genome_file,
            name=name,
            max_evalue=max_evalue,
            min_coverage=min_coverage,
            min_pident=min_pident,
            prefix_remove=prefix_remove,
            suffix_remove=suffix_remove,
            cache_blast_results=cache_blast_results,
        )

    def create_submodel_from_sequences_and_proteome(
        self,
        sequences: Iterable[str],
        proteome_file: str | Path,
        name: str | None = None,
        max_evalue: float = 1e-6,
        min_coverage: float = 85,
        min_pident: float = 85,
        prefix_remove: str = r"gnl\|.*?\|",
        suffix_remove: str = None,
        cache_blast_results: bool = False,
    ) -> "Model":
        if cache_blast_results:
            if name is None:
                raise ValueError("Name has to be given in order to cache results")
            blast_file = get_temporary_directory(subdirectory="blast") / f"blast_proteome_monomers_{name}.csv"
            if blast_file.is_file():
                blast_monomers = pd.read_csv(blast_file, index_col=0)
            else:
                print(f"Caching results to {blast_file}")
                blast_monomers = self.blast_sequences_against_proteome(
                    sequences=sequences, proteome_file=proteome_file
                )
                blast_monomers.to_csv(blast_file)
        else:
            blast_monomers = self.blast_sequences_against_proteome(
                sequences=sequences, proteome_file=proteome_file
            )
        return self.create_submodel_from_blast_monomers(
            blast_monomers=blast_monomers,
            name=name,
            max_evalue=max_evalue,
            min_coverage=min_coverage,
            min_pident=min_pident,
            prefix_remove=prefix_remove,
            suffix_remove=suffix_remove,
        )

    def create_submodel_from_proteome(
        self,
        proteome_file: str | Path,
        name: str | None = None,
        max_evalue: float = 1e-6,
        min_coverage: float = 85,
        min_pident: float = 85,
        prefix_remove: str = r"gnl\|.*?\|",
        suffix_remove: str = None,
        cache_blast_results: bool = False,
    ) -> "Model":
        return self.create_submodel_from_sequences_and_proteome(
            self.get_all_monomer_sequences(),
            proteome_file=proteome_file,
            name=name,
            max_evalue=max_evalue,
            min_coverage=min_coverage,
            min_pident=min_pident,
            prefix_remove=prefix_remove,
            suffix_remove=suffix_remove,
            cache_blast_results=cache_blast_results,
        )

    ##########################################################################
    # Serde
    ##########################################################################

    def to_sbml(self, filename: str | Path = "model.sbml") -> None:
        """Export the model to sbml."""
        doc = _export_model(model=self)
        libsbml.writeSBMLToFile(doc, filename=str(filename))

    def to_pickle(self, filename: str | Path) -> None:
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    def to_json(self, filename: str | Path) -> None:
        from ..utils.serialize import serialize

        with open(filename, "w") as file:
            json.dump(serialize(self), file, indent=2)

    def to_yaml(self, filename: str | Path) -> None:
        from ..utils.serialize import serialize

        with open(filename, "w") as file:
            yaml.dump(serialize(self), file)

    @staticmethod
    def load_from_pickle(filename: str | Path) -> "Model":
        with open(filename, "rb") as file:
            model = pickle.load(file)
        if isinstance(model, Model):
            return model
        raise NotImplementedError("Pickled object is not a Model")

    @staticmethod
    def load_from_json(filename: str | Path) -> "Model":
        with open(filename, "r") as file:
            obj = json.load(file)
        return _deserialize(obj)

    @staticmethod
    def load_from_yaml(filename: str | Path) -> "Model":
        with open(filename, "r") as file:
            obj = yaml.safe_load(file)
        return _deserialize(obj)


def _deserialize_compounds(obj: Dict[str, Any]) -> list[Compound]:
    return [
        Compound(
            base_id=str(i["base_id"]),
            id=str(i["id"]),
            name=str(i["name"]),
            compartment=str(i["compartment"]),
            smiles=str(i["smiles"]),
            formula={str(k): float(v) for k, v in i["formula"].items()},
            charge=int(charge) if (charge := i["charge"]) is not None else None,
            gibbs0=float(gibbs0) if (gibbs0 := i["gibbs0"]) is not None else None,
            database_links={str(k): set(v) for k, v in i["database_links"].items()},
            types=list(i["types"]),
            in_reaction=set(i["in_reaction"]),
        )
        for i in obj["compounds"]
    ]


def _deserialize_reactions(obj: Dict[str, Any]) -> list[Reaction]:
    return [
        Reaction(
            base_id=str(i["base_id"]),
            id=str(i["id"]),
            name=str(name) if (name := i["name"]) is not None else None,
            compartment=str(comp)
            if isinstance(comp := i["compartment"], str)
            else tuple(str(x) for x in comp),
            bounds=(float(i["bounds"][0]), float(i["bounds"][1])),
            gibbs0=float(gibbs0) if (gibbs0 := i["gibbs0"]) is not None else None,
            ec=i["ec"],
            transmembrane=i["transmembrane"] == "True",
            types=list(i["types"]),
            pathways=set(i["pathways"]),
            stoichiometries={k: float(v) for k, v in i["stoichiometries"].items()},
            gpr_annotation=[set(v) for v in i["gpr_annotation"]],
            kinetic_data={k: KineticData(**v) for k, v in i["kinetic_data"].items()},
            database_links={k: set(v) for k, v in i["database_links"].items()},
        )
        for i in obj["reactions"]
    ]


def _deserialize(obj: Dict[str, Any]) -> Model:
    return Model(
        compounds=_deserialize_compounds(obj),
        reactions=_deserialize_reactions(obj),
        compartments=obj["compartments"],
        objective=obj["objective"],
        minimal_seed=set(obj["minimal_seed"]),
        name=obj["name"],
        cofactor_pairs=obj["base_cofactor_pairs"],
    )
