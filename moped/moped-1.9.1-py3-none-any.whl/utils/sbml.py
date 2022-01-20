from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Iterable, Union

import libsbml

if TYPE_CHECKING:
    from .. import Compound, Model, Reaction
    from ..core.monomer import Monomer

__all__ = [
    "export_units",
    "export_compartments",
    "export_compounds",
    "export_genes",
    "export_objective",
    "export_reactions",
    "export_model",
]


@dataclass
class Unit:
    kind: libsbml.UnitDefinition
    scale: int
    multiplier: int
    exponent: int


@dataclass
class UnitDefinition:
    name: str
    units: Iterable[Unit]


SBML_DOT = "__SBML_DOT__"
RE_TO_SBML = re.compile(r"([^0-9_a-zA-Z])")


def _escape_non_alphanum(non_ascii: re.Match) -> str:
    """converts a non alphanumeric character to a string representation of
    its ascii number"""
    return "__" + str(ord(non_ascii.group())) + "__"


def _format_name_to_sbml(sid: str, prefix: str = "") -> str:
    sid = RE_TO_SBML.sub(_escape_non_alphanum, sid)
    sid = sid.replace(".", SBML_DOT)
    return f"{prefix}{sid}"


def _check_libsbml_str_setter(function: Callable[[str], Any], input1: str) -> None:
    """Instead of erroring, libsbml only returns status flags.
    Splitting these functions by type to at least get typing. Super annoying.
    """
    if not function(input1) == libsbml.LIBSBML_OPERATION_SUCCESS:
        warnings.warn(f"Failed writing attribute {input1} for {function.__name__}")


def _check_libsbml_bool_setter(function: Callable[[bool], Any], input1: bool) -> None:
    """Instead of erroring, libsbml only returns status flags.
    Splitting these functions by type to at least get typing. Super annoying.
    """
    if not function(input1) == libsbml.LIBSBML_OPERATION_SUCCESS:
        warnings.warn(f"Failed writing attribute {input1} for {function.__name__}")


def _check_libsbml_any_setter(function: Callable[[Any], Any], input1: Any) -> None:
    """Instead of erroring, libsbml only returns status flags.
    Splitting these functions by type to at least get typing. Super annoying.
    This one is for libsbml internal fields, which are all just Any
    """
    if not function(input1) == libsbml.LIBSBML_OPERATION_SUCCESS:
        warnings.warn(f"Failed writing attribute {input1} for {function.__name__}")


def _check_libsbml_float_setter(function: Callable[[float], Any], input1: float) -> None:
    """Instead of erroring, libsbml only returns status flags.
    Splitting these functions by type to at least get typing. Super annoying.
    This one is for libsbml internal fields, which are all just Any
    """
    if not function(input1) == libsbml.LIBSBML_OPERATION_SUCCESS:
        warnings.warn(f"Failed writing attribute {input1} for {function.__name__}")


def _check_libsbml_int_setter(function: Callable[[int], Any], input1: int) -> None:
    """Instead of erroring, libsbml only returns status flags.
    Splitting these functions by type to at least get typing. Super annoying.
    This one is for libsbml internal fields, which are all just Any
    """
    if not function(input1) == libsbml.LIBSBML_OPERATION_SUCCESS:
        warnings.warn(f"Failed writing attribute {input1} for {function.__name__}")


def _check_libsbml_str_bool_setter(function: Callable[[str, bool], Any], input1: str, input2: bool) -> None:
    if not function(input1, input2) == libsbml.LIBSBML_OPERATION_SUCCESS:
        warnings.warn(f"Failed writing attributes {input1}, {input2} for {function.__name__}")


def _check_libsbml_str_int_setter(function: Callable[[str, int], Any], input1: str, input2: int) -> None:
    if not function(input1, input2) == libsbml.LIBSBML_OPERATION_SUCCESS:
        warnings.warn(f"Failed writing attributes {input1}, {input2} for {function.__name__}")


def _check_libsbml_str_bool_bool_setter(
    function: Callable[[str, bool, bool], Any], input1: str, input2: bool, input3: bool
) -> None:
    """Instead of erroring, libsbml only returns status flags.
    Splitting these functions by type to at least get typing. Super annoying.
    """
    if not function(input1, input2, input3) == libsbml.LIBSBML_OPERATION_SUCCESS:
        warnings.warn(f"Failed writing attributes {input1}, {input2}, {input3} for {function.__name__}")


def export_model_name(model: "Model", sbml_model: libsbml.Model) -> None:
    if model.name is not None:
        name = _format_name_to_sbml(model.name)
        _check_libsbml_str_setter(sbml_model.setId, name)
        _check_libsbml_str_setter(sbml_model.setMetaId, f"meta_{name}")
        _check_libsbml_str_setter(sbml_model.setName, name)
    else:
        _check_libsbml_str_setter(sbml_model.setMetaId, "meta_model")


def export_model_annotations(model: "Model", sbml_model: libsbml.Model) -> None:
    raise NotImplementedError


def export_model_notes(model: "Model", sbml_model: libsbml.Model) -> None:
    raise NotImplementedError


def export_model_meta_data(model: "Model", sbml_model: libsbml.Model) -> None:
    raise NotImplementedError


def export_units(model: "Model", sbml_model: libsbml.Model) -> None:
    default = UnitDefinition(
        name="mmol_per_gDW_per_hr",
        units=[
            Unit(
                kind=libsbml.UNIT_KIND_MOLE,
                scale=-3,
                multiplier=1,
                exponent=1,
            ),
            Unit(
                kind=libsbml.UNIT_KIND_GRAM,
                scale=0,
                multiplier=1,
                exponent=-1,
            ),
            Unit(
                kind=libsbml.UNIT_KIND_SECOND,
                scale=0,
                multiplier=3600,
                exponent=-1,
            ),
        ],
    )

    flux_udef: libsbml.UnitDefinition = sbml_model.createUnitDefinition()
    _check_libsbml_str_setter(flux_udef.setId, _format_name_to_sbml(default.name))
    for u in default.units:
        unit: libsbml.Unit = flux_udef.createUnit()
        _check_libsbml_any_setter(unit.setKind, u.kind)
        _check_libsbml_int_setter(unit.setExponent, u.exponent)
        _check_libsbml_int_setter(unit.setScale, u.scale)
        _check_libsbml_float_setter(unit.setMultiplier, u.multiplier)


def export_compartments(model: "Model", sbml_model: libsbml.Model) -> None:
    for name, suffix in model.compartments.items():
        compartment: libsbml.Compartment = sbml_model.createCompartment()
        _check_libsbml_str_setter(compartment.setId, _format_name_to_sbml(suffix))
        _check_libsbml_str_setter(compartment.setName, name)
        _check_libsbml_bool_setter(compartment.setConstant, True)


def _add_identifier_annotation(
    element: Union["Compound", "Reaction", "Monomer"],
    sbml_element: Union[libsbml.Species, libsbml.Reaction, libsbml.GeneProduct],
) -> None:
    for db, data in element.database_links.items():
        for item in data:
            cv: libsbml.CVTerm = libsbml.CVTerm()
            _check_libsbml_any_setter(cv.setQualifierType, libsbml.BIOLOGICAL_QUALIFIER)
            _check_libsbml_any_setter(cv.setBiologicalQualifierType, libsbml.BQB_IS)
            _check_libsbml_str_setter(cv.addResource, f"https://identifiers.org/{db}:{item}")
            _check_libsbml_any_setter(sbml_element.addCVTerm, cv)


def export_compounds(model: "Model", sbml_model: libsbml.Model) -> None:
    for cpd in model.compounds.values():
        specie: libsbml.Species = sbml_model.createSpecies()
        cpd_id = _format_name_to_sbml(cpd.id, "M_")
        _check_libsbml_str_setter(specie.setId, cpd_id)
        _check_libsbml_str_setter(specie.setMetaId, f"meta_{cpd_id}")  # needed for annotations
        if (name := cpd.name) is not None:
            _check_libsbml_str_setter(specie.setName, name)
        _check_libsbml_bool_setter(specie.setConstant, False)
        _check_libsbml_bool_setter(specie.setBoundaryCondition, False)
        _check_libsbml_bool_setter(specie.setHasOnlySubstanceUnits, False)
        _check_libsbml_str_setter(specie.setCompartment, model.compartments[cpd.compartment])

        s_fbc: libsbml.FbcSpeciesPlugin = specie.getPlugin("fbc")
        if cpd.charge is not None:
            _check_libsbml_int_setter(s_fbc.setCharge, int(cpd.charge))
        if cpd.formula is not None:
            _check_libsbml_str_setter(s_fbc.setChemicalFormula, cpd.formula_to_string())

        # database links
        _add_identifier_annotation(element=cpd, sbml_element=specie)

        # SBO
        _check_libsbml_str_setter(specie.setSBOTerm, "SBO:0000247")  # general metabolite


def export_genes(model: "Model", sbml_model: libsbml.Model) -> None:
    model_fbc: libsbml.FbcModelPlugin = sbml_model.getPlugin("fbc")
    # genes: Set[str] = set()
    for monomer in model.monomers.values():
        name = monomer.id
        # if name in genes:
        #     continue
        # genes.add(name)
        gene_id = _format_name_to_sbml(name, "G_")
        gp: libsbml.GeneProduct = model_fbc.createGeneProduct()
        _check_libsbml_str_setter(gp.setId, gene_id)
        _check_libsbml_str_setter(gp.setMetaId, f"meta_{gene_id}")
        _check_libsbml_str_setter(gp.setLabel, gene_id)
        _add_identifier_annotation(element=monomer, sbml_element=gp)

        # SBO
        _check_libsbml_str_setter(gp.setSBOTerm, "SBO:0000243")  # general gene


def export_objective(model: "Model", sbml_model: libsbml.Model) -> None:
    model_fbc: libsbml.FbcModelPlugin = sbml_model.getPlugin("fbc")
    objective: libsbml.Objective = model_fbc.createObjective()
    _check_libsbml_str_setter(objective.setId, "obj")
    _check_libsbml_str_setter(objective.setType, "maximize")
    _check_libsbml_str_setter(model_fbc.setActiveObjectiveId, "obj")

    if not bool(model.objective):
        raise ValueError("Exporting model without objective. This won't lead to a valid SBML.")

    for rid, coef in model.objective.items():
        flux_obj: libsbml.FluxObjective = objective.createFluxObjective()
        _check_libsbml_str_setter(flux_obj.setReaction, _format_name_to_sbml(rid, "R_"))
        _check_libsbml_float_setter(flux_obj.setCoefficient, float(coef))


def _create_bound_parameter(
    reaction_id: str,
    sbml_model: libsbml.Model,
    bound: float,
    lower: bool,
    r_fbc: libsbml.FbcReactionPlugin,
) -> None:
    par: libsbml.Parameter = sbml_model.createParameter()
    _check_libsbml_float_setter(par.setValue, bound)
    _check_libsbml_bool_setter(par.setConstant, True)
    _check_libsbml_str_setter(par.setSBOTerm, "SBO:0000625")
    if lower:
        pid = f"{reaction_id}_lower"
        _check_libsbml_str_setter(par.setId, pid)
        _check_libsbml_str_setter(r_fbc.setLowerFluxBound, pid)
    else:
        pid = f"{reaction_id}_upper"
        _check_libsbml_str_setter(par.setId, pid)
        _check_libsbml_str_setter(r_fbc.setUpperFluxBound, pid)


def export_reactions(model: "Model", sbml_model: libsbml.Model) -> None:
    for reaction in model.reactions.values():
        sbml_rxn: libsbml.Reaction = sbml_model.createReaction()
        r_fbc: libsbml.FbcReactionPlugin = sbml_rxn.getPlugin("fbc")

        sbml_rxn_id = _format_name_to_sbml(reaction.id, "R_")
        _check_libsbml_str_setter(sbml_rxn.setId, sbml_rxn_id)
        _check_libsbml_str_setter(sbml_rxn.setMetaId, f"meta_{sbml_rxn_id}")
        if (name := reaction.name) is not None:
            _check_libsbml_str_setter(sbml_rxn.setName, name)
        _check_libsbml_bool_setter(sbml_rxn.setFast, False)
        if (reversible := reaction.reversible) is not None:
            _check_libsbml_bool_setter(sbml_rxn.setReversible, reversible)

        # Stoichiometries
        for species, stoichiometry in reaction.stoichiometries.items():
            if stoichiometry < 0:
                sref: libsbml.SpeciesReference = sbml_rxn.createReactant()
                _check_libsbml_float_setter(sref.setStoichiometry, -float(stoichiometry))
            else:
                sref = sbml_rxn.createProduct()
                _check_libsbml_float_setter(sref.setStoichiometry, float(stoichiometry))
            _check_libsbml_str_setter(sref.setSpecies, _format_name_to_sbml(species, "M_"))
            _check_libsbml_bool_setter(sref.setConstant, True)

        # Bounds
        if (bounds := reaction.bounds) is not None:
            _create_bound_parameter(
                reaction_id=sbml_rxn_id,
                sbml_model=sbml_model,
                r_fbc=r_fbc,
                bound=bounds[0],
                lower=True,
            )
            _create_bound_parameter(
                reaction_id=sbml_rxn_id,
                sbml_model=sbml_model,
                r_fbc=r_fbc,
                bound=bounds[1],
                lower=False,
            )

        # GPR
        if (gene_id := reaction._gpa) is not None:
            gpa_id = _format_name_to_sbml(reaction.id, "GA_")
            genes = [_format_name_to_sbml(name, "G_") for name in reaction.gpr_annotation[gene_id]]
            if len(genes) > 0:
                gpa: libsbml.GeneProductAssociation = r_fbc.createGeneProductAssociation()
                _check_libsbml_str_setter(gpa.setId, gpa_id)
                _check_libsbml_str_setter(gpa.setMetaId, f"meta_{gpa_id}")
                _check_libsbml_str_setter(gpa.setName, gpa_id)
                # string_association, usingId=True, addMissingGP=False
                _check_libsbml_str_bool_bool_setter(gpa.setAssociation, " and ".join(genes), True, False)
                _check_libsbml_str_setter(gpa.setSBOTerm, "SBO:0000243")  # general gene

        # Database Links
        _add_identifier_annotation(element=reaction, sbml_element=sbml_rxn)

        # SBO
        if reaction.transmembrane:
            _check_libsbml_str_setter(sbml_rxn.setSBOTerm, "SBO:0000185")  # transport reaction
        elif reaction.id.startswith("EX_"):
            _check_libsbml_str_setter(sbml_rxn.setSBOTerm, "SBO:0000627")  # exchange reaction
        elif reaction.id in model.objective:
            _check_libsbml_str_setter(sbml_rxn.setSBOTerm, "SBO:0000629")  # exchange reaction
        else:
            _check_libsbml_str_setter(sbml_rxn.setSBOTerm, "SBO:0000176")  # general reaction


def export_model(model: "Model") -> libsbml.SBMLDocument:
    sbml_ns = libsbml.SBMLNamespaces(3, 1)  # SBML L3V1
    _check_libsbml_str_int_setter(sbml_ns.addPackageNamespace, "fbc", 2)

    doc: libsbml.SBMLDocument = libsbml.SBMLDocument(sbml_ns)
    _check_libsbml_str_bool_setter(doc.setPackageRequired, "fbc", False)
    _check_libsbml_str_setter(doc.setSBOTerm, "SBO:0000624")

    sbml_model: libsbml.Model = doc.createModel()
    model_fbc: libsbml.FbcModelPlugin = sbml_model.getPlugin("fbc")
    _check_libsbml_bool_setter(model_fbc.setStrict, True)

    export_model_name(model, sbml_model)
    # export_model_annotations(model, sbml_model)
    # export_model_notes(model, sbml_model)
    # export_model_meta_data(model, sbml_model)
    export_units(model, sbml_model)
    export_compartments(model, sbml_model)
    export_compounds(model, sbml_model)
    export_genes(model, sbml_model)
    export_reactions(model, sbml_model)
    export_objective(model, sbml_model)
    return doc
