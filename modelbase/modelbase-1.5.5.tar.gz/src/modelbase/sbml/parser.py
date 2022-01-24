from __future__ import annotations

__all__ = [
    "Parser",
]

import copy
import math
import re
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, cast

import libsbml
import numpy as np
import numpy.typing as npt
import sympy

from ..ode import Model
from .data import (
    AlgebraicRule,
    AssignmentRule,
    AtomicUnit,
    Compartment,
    CompositeUnit,
    Compound,
    Function,
    InitialAssignment,
    Parameter,
    RateRule,
    Reaction,
)
from .mathml import handle_ast_node
from .unit_conversion import get_operator_mappings, get_unit_conversion

UNIT_CONVERSION = get_unit_conversion()
OPERATOR_MAPPINGS = get_operator_mappings()
INDENT = "    "


def _simplify_function_body(function_body: str) -> str:
    try:
        function_body = str(sympy.parse_expr(function_body))
    except AttributeError:
        pass
    except TypeError:
        pass
    return function_body


class Parser:
    """
    Stages:
        - raw parsing
        - mapping
            - compounds -> parameters
            - rate_rule -> reaction
            - algebraic_rule -> assignment_rule
        - fixing (function args)
        - conversion into python / modelbase objects
    """

    def _raise_or_warn(self, msg: str, error: Type[RuntimeError]) -> None:
        if self.raise_warnings:
            raise error(msg)
        warnings.warn(msg)

    def __init__(self, file: Union[str, Path], raise_warnings: bool = True) -> None:
        self.raise_warnings = raise_warnings

        if not Path(file).exists():
            raise IOError("Model file does not exist")
        doc: libsbml.SBML_DOCUMENT = libsbml.readSBMLFromFile(str(file))

        # Check for unsupported packages
        for i in range(doc.num_plugins):
            if doc.getPlugin(i).getPackageName() == "comp":
                self._raise_or_warn("No support for comp package", NotImplementedError)

        self.sbml_model = doc.getModel()
        if bool(self.sbml_model.getConversionFactor()):
            self._raise_or_warn("Conversion factors are currently not supported", NotImplementedError)

        # Collections
        self.produced_compounds: set[str] = set()
        self.consumed_compounds: set[str] = set()
        self.derived_compounds: set[str] = set()
        self.boundary_species: set[str] = set()
        # Parsed stuff
        self.parsed_atomic_units: Dict[str, AtomicUnit] = {}
        self.parsed_units: Dict[str, CompositeUnit] = {}
        self.parsed_parameters: Dict[str, Parameter] = {}
        self.parsed_initial_assignments: Dict[str, InitialAssignment] = {}
        self.parsed_compartments: Dict[str, Compartment] = {}
        self.parsed_species: Dict[str, Compound] = {}
        self.parsed_functions: Dict[str, Function] = {}
        self.parsed_algebraic_rules: Dict[str, AlgebraicRule] = {}
        self.parsed_assignment_rules: Dict[str, AssignmentRule] = {}
        self.parsed_rate_rules: Dict[str, RateRule] = {}
        self.parsed_reactions: Dict[str, Reaction] = {}

        # Converted intermediates
        self.converted_initial_assignments: Dict[str, InitialAssignment] = {}
        self.converted_functions: Dict[str, Function] = {}
        self.converted_variables: Dict[str, Compound] = {}
        self.converted_constants: Dict[str, Parameter] = {}
        self.converted_derived_constants: Dict[str, InitialAssignment] = {}
        self.converted_reactions: Dict[str, Reaction] = {}
        self.converted_algebraic_modules: Dict[str, AssignmentRule] = {}

    ###############################################################################
    # PARSING STAGE
    ###############################################################################

    def parse_constraints(self) -> None:
        if len(self.sbml_model.getListOfConstraints()) > 0:
            warnings.warn(
                "modelbase does not support model constraints. "
                "Check the file for hints of the range of stable solutions."
            )

    def parse_events(self) -> None:
        if len(self.sbml_model.getListOfEvents()) > 0:
            self._raise_or_warn("modelbase does not currently support events.", NotImplementedError)

    def parse_units(self) -> None:
        for unit_definition in self.sbml_model.getListOfUnitDefinitions():
            composite_id = unit_definition.getId()
            local_units = []
            for unit in unit_definition.getListOfUnits():
                atomic_unit = AtomicUnit(
                    kind=UNIT_CONVERSION[unit.getKind()],
                    scale=unit.getScale(),
                    exponent=unit.getExponent(),
                    multiplier=unit.getMultiplier(),
                )
                local_units.append(atomic_unit.kind)
                self.parsed_atomic_units[atomic_unit.kind] = atomic_unit
            self.parsed_units[composite_id] = CompositeUnit(
                sbml_id=composite_id,
                units=local_units,
            )

    def parse_initial_assignments(self) -> None:
        for assignment in self.sbml_model.getListOfInitialAssignments():
            sbml_id = assignment.getId()
            node = assignment.getMath()
            if node is None:
                continue
            sbml_math = libsbml.formulaToL3String(node)
            parsed_arguments: List[str] = []
            function_body = handle_ast_node(node, parsed_arguments)
            parsed_arguments = sorted(set(parsed_arguments))
            self.parsed_initial_assignments[sbml_id] = InitialAssignment(
                sbml_id=sbml_id,
                derived_parameter=assignment.getSymbol(),
                function_args=parsed_arguments,
                function_body=function_body,
                sbml_math=sbml_math,
            )

    def parse_parameters(self) -> None:
        for parameter in self.sbml_model.getListOfParameters():
            parameter_id = parameter.getId()
            self.parsed_parameters[parameter_id] = Parameter(
                sbml_id=parameter_id,
                name=parameter.getName(),
                value=parameter.getValue(),
                is_constant=parameter.getConstant(),
            )

    def parse_compartments(self) -> None:
        for compartment in self.sbml_model.getListOfCompartments():
            sbml_id = compartment.getId()
            size = compartment.getSize()
            if str(size) == "nan":
                size = 0
            self.parsed_compartments[sbml_id] = Compartment(
                sbml_id=sbml_id,
                name=compartment.getName(),
                dimensions=compartment.getSpatialDimensions(),
                size=size,
                units=compartment.getUnits(),
                is_constant=compartment.getConstant(),
            )

    def parse_species(self) -> None:
        for compound in self.sbml_model.getListOfSpecies():
            if bool(compound.getConversionFactor()):
                self._raise_or_warn("Conversion factors are not supported", NotImplementedError)
            compound_id = compound.getId()
            initial_amount = compound.getInitialAmount()
            if str(initial_amount) == "nan":
                initial_amount = compound.getInitialConcentration()
                if str(initial_amount) == "nan":
                    is_concentration = False
                else:
                    is_concentration = True
            else:
                is_concentration = False

            has_boundary_condition = compound.getBoundaryCondition()
            if has_boundary_condition:
                self.boundary_species.add(compound_id)

            self.parsed_species[compound_id] = Compound(
                sbml_id=compound_id,
                name=compound.getName(),
                compartment=compound.getCompartment(),
                initial_amount=initial_amount,
                substance_units=compound.getSubstanceUnits(),
                has_only_substance_units=compound.getHasOnlySubstanceUnits(),
                has_boundary_condition=has_boundary_condition,
                is_constant=compound.getConstant(),
                is_concentration=is_concentration,
            )

    def parse_functions(self) -> None:
        for func in self.sbml_model.getListOfFunctionDefinitions():
            func_name = func.getName()
            sbml_id = func.getId()
            if sbml_id is None or sbml_id == "":
                sbml_id = func_name
            elif func_name is None or func_name == "":
                func_name = sbml_id

            parsed_arguments: List[str] = []
            node = func.getMath()
            if node is None:
                continue
            body = handle_ast_node(node=node, func_arguments=parsed_arguments)
            parsed_arguments = sorted(set(parsed_arguments))

            self.parsed_functions[func_name] = Function(
                sbml_id=sbml_id,
                name=func_name,
                function_args=parsed_arguments,
                function_body=body,
                sbml_math=libsbml.formulaToL3String(node),
            )

    def _parse_algebraic_rule(self, rule: libsbml.AlgebraicRule) -> None:
        node = rule.getMath()
        if node is None:
            return None
        sbml_id = rule.getMetaId()
        sbml_math = libsbml.formulaToL3String(node)

        parsed_arguments: List[str] = []
        parsed_node = handle_ast_node(node, parsed_arguments)
        parsed_arguments = sorted(set(parsed_arguments))

        self.parsed_algebraic_rules[sbml_id] = AlgebraicRule(
            sbml_id=sbml_id,
            sbml_math=sbml_math,
            parsed_args=parsed_arguments,
            derived_compound=None,
            function_body=parsed_node,
            function_args=[],
        )

    def _parse_assignment_rule(self, rule: libsbml.AssignmentRule) -> None:
        node = rule.getMath()
        if node is None:
            return None

        sbml_id: Optional[str] = rule.getMetaId()
        sbml_math: str = libsbml.formulaToL3String(node)
        derived_compound: str = rule.getId()

        if sbml_id is None or sbml_id == "":
            sbml_id = derived_compound

        parsed_arguments: List[str] = []
        parsed_node = handle_ast_node(node=node, func_arguments=parsed_arguments)
        parsed_arguments = sorted(set(parsed_arguments))

        self.parsed_assignment_rules[sbml_id] = AssignmentRule(
            sbml_id=sbml_id,
            sbml_math=sbml_math,
            parsed_args=parsed_arguments,
            compounds=[],
            modifiers=[],
            derived_compound=derived_compound,
            parameters=[],
            function_body=parsed_node,
            function_args=[],
        )

    def _parse_rate_rule(self, rule: libsbml.RateRule) -> None:
        sbml_id = rule.getMetaId()
        derived_compound = rule.getId()
        if sbml_id is None or sbml_id == "":
            sbml_id = derived_compound
        node = rule.getMath()
        if node is None:
            return None
        sbml_math = libsbml.formulaToL3String(node)

        parsed_arguments: List[str] = []
        parsed_node = handle_ast_node(node=node, func_arguments=parsed_arguments)
        parsed_arguments = sorted(set(parsed_arguments))

        if derived_compound not in self.parsed_species:
            self._raise_or_warn("RateRule may only target species", NotImplementedError)

        self.parsed_rate_rules[sbml_id] = RateRule(
            sbml_id=sbml_id,
            sbml_math=sbml_math,
            parsed_args=parsed_arguments,
            derived_compound=derived_compound,
            modifiers=[],
            function_body=parsed_node,
            function_args=[],
        )

    def parse_rules(self) -> None:
        """Parse rules and separate them by type"""
        for rule in self.sbml_model.getListOfRules():
            if rule.element_name == "algebraicRule":
                self._parse_algebraic_rule(rule=rule)
            elif rule.element_name == "assignmentRule":
                self._parse_assignment_rule(rule=rule)
            elif rule.element_name == "rateRule":
                self._parse_rate_rule(rule=rule)
            else:
                raise ValueError("Unknown rate type")

    def _parse_local_parameters(self, reaction_id: str, kinetic_law: libsbml.KineticLaw) -> Dict[str, str]:
        """Parse local parameters"""
        parameters_to_update = {}
        for parameter in kinetic_law.getListOfLocalParameters():
            old_id = parameter.getId()
            if old_id in self.parsed_parameters:
                new_id = f"{reaction_id}__{old_id}"
                parameters_to_update[old_id] = new_id
            else:
                new_id = old_id
            self.parsed_parameters[new_id] = Parameter(
                sbml_id=new_id,
                name=parameter.getName(),
                value=parameter.getValue(),
                is_constant=parameter.getConstant(),
            )
        # Some models apparently also write local parameters in this
        for parameter in kinetic_law.getListOfParameters():
            old_id = parameter.getId()
            if old_id in self.parsed_parameters:
                new_id = f"{reaction_id}__{old_id}"
                parameters_to_update[old_id] = new_id
            else:
                new_id = old_id
            self.parsed_parameters[new_id] = Parameter(
                sbml_id=new_id,
                name=parameter.getName(),
                value=parameter.getValue(),
                is_constant=parameter.getConstant(),
            )
        return parameters_to_update

    def parse_reactions(self) -> None:
        for reaction in self.sbml_model.getListOfReactions():
            sbml_id = reaction.getId()
            kinetic_law = reaction.getKineticLaw()
            if kinetic_law is None:
                continue
            parameters_to_update = self._parse_local_parameters(reaction_id=sbml_id, kinetic_law=kinetic_law)

            node = reaction.getKineticLaw().getMath()
            sbml_math = libsbml.formulaToL3String(node)
            is_reversible = reaction.getReversible()
            modifiers = [i.getSpecies() for i in reaction.getListOfModifiers()]

            parsed_arguments: List[str] = []
            parsed_node = handle_ast_node(node=node, func_arguments=parsed_arguments)
            parsed_arguments = sorted(set(parsed_arguments))

            # Update parameter references
            for old, new in parameters_to_update.items():
                pat = re.compile(f"({old})" + r"\b")
                parsed_node = pat.sub(new, parsed_node)
                sbml_math = pat.sub(new, parsed_node)
            for i, arg in enumerate(parsed_arguments):
                parsed_arguments[i] = parameters_to_update.get(arg, arg)

            parsed_reactants: defaultdict[str, int] = defaultdict(int)
            for substrate in reaction.getListOfReactants():
                species = substrate.getSpecies()
                if species not in self.boundary_species:
                    stoichiometry = substrate.getStoichiometry()
                    if str(stoichiometry) == "nan":
                        self._raise_or_warn("Cannot parse stoichiometry", NotImplementedError)
                    parsed_reactants[species] -= stoichiometry
            parsed_products: defaultdict[str, int] = defaultdict(int)
            for product in reaction.getListOfProducts():
                species = product.getSpecies()
                if species not in self.boundary_species:
                    stoichiometry = product.getStoichiometry()
                    if str(stoichiometry) == "nan":
                        self._raise_or_warn("Cannot parse stoichiometry", NotImplementedError)
                    parsed_products[species] += stoichiometry

            self.parsed_reactions[sbml_id] = Reaction(
                sbml_id=sbml_id,
                sbml_math=sbml_math,
                is_reversible=is_reversible,
                modifiers=modifiers,
                parsed_args=parsed_arguments,
                parsed_reactants=dict(parsed_reactants),
                parsed_products=dict(parsed_products),
                function_body=parsed_node,
                function_args=[],
                parameters=[],
                stoichiometry={},
            )

    def _parse(self) -> None:
        self.parse_functions()
        self.parse_units()
        self.parse_compartments()
        self.parse_species()
        self.parse_parameters()
        self.parse_initial_assignments()
        self.parse_rules()
        self.parse_constraints()
        self.parse_reactions()
        self.parse_events()

    ###############################################################################
    # Collection & conversion stage
    ###############################################################################

    def collect_slow_changing_compounds(self) -> None:
        """Needed for algebraic rules to find out which
        variable is the fast-changing on"""
        for reaction in self.parsed_reactions.values():
            for i in reaction.parsed_products:
                self.produced_compounds.add(i)
            for i in reaction.parsed_reactants:
                self.consumed_compounds.add(i)
        for rate in self.parsed_rate_rules.values():
            self.produced_compounds.add(rate.derived_compound)

    def _move_parameter_to_variables(self, parameter: Parameter) -> None:
        self.converted_variables[parameter.sbml_id] = Compound(
            sbml_id=parameter.sbml_id,
            name=parameter.name,
            compartment=None,
            initial_amount=parameter.value,
            substance_units=None,
            has_only_substance_units=True,
            has_boundary_condition=False,
            is_constant=parameter.is_constant,
            is_concentration=False,
        )

    def _move_compartment_to_constants(self, compartment: Compartment) -> None:
        self.converted_constants[compartment.sbml_id] = Parameter(
            sbml_id=compartment.sbml_id,
            name=compartment.name,
            value=compartment.size,
            is_constant=compartment.is_constant,
        )

    def _move_compartment_to_variables(self, compartment: Compartment) -> None:
        self.converted_variables[compartment.sbml_id] = Compound(
            sbml_id=compartment.sbml_id,
            name=compartment.name,
            compartment=compartment.sbml_id,
            initial_amount=compartment.size,
            substance_units=compartment.units,
            has_only_substance_units=True,
            has_boundary_condition=False,
            is_constant=compartment.is_constant,
            is_concentration=False,
        )

    def _move_compound_to_constants(self, compound: Compound) -> None:
        self.converted_constants[compound.sbml_id] = Parameter(
            sbml_id=compound.sbml_id,
            name=compound.name,
            value=compound.initial_amount,
            is_constant=compound.is_constant,
        )

    def convert_parameters(self) -> None:
        for sbml_id, parameter in self.parsed_parameters.items():
            if not parameter.is_constant:
                self._move_parameter_to_variables(parameter=parameter)
            else:
                self.converted_constants[sbml_id] = parameter

    def convert_compartments(self) -> None:
        for compartment in self.parsed_compartments.values():
            if compartment.is_constant:
                self._move_compartment_to_constants(compartment=compartment)
            else:
                self._move_compartment_to_variables(compartment=compartment)

    def convert_compounds(self) -> None:
        for sbml_id, compound in self.parsed_species.items():
            if compound.is_constant:
                self._move_compound_to_constants(compound=compound)
            else:
                self.converted_variables[sbml_id] = compound

    def _replace_function_with_operators(self, algebraic_rule: AlgebraicRule) -> None:
        rule_body = algebraic_rule.function_body
        if "," not in rule_body:
            return None

        for func_id, function in self.parsed_functions.items():
            func_pattern = re.compile(f"{func_id}\(.+\)")
            matches = re.findall(func_pattern, rule_body)
            for match in matches:
                func_body = function.function_body
                func_args = function.function_args
                parts = match[len(f"{func_id}(") : -1].split(", ")
                for arg, repl in zip(func_args, parts):
                    func_body = re.sub(arg, f"({repl})", func_body)
                rule_body = re.sub(func_pattern, func_body, rule_body)

        algebraic_rule.function_body = rule_body

    def _convert_algebraic_to_assignment_rule(self, rule: AlgebraicRule) -> None:
        parsed_args = rule.parsed_args
        # isolate derived_compound
        explained_args = self.produced_compounds | set(self.converted_constants)
        unexplained_args = list(set(parsed_args).difference(explained_args))
        if len(unexplained_args) > 1:
            unexplained_args = list(set(unexplained_args).difference(self.consumed_compounds))
            if len(unexplained_args) > 1:
                self._raise_or_warn("No handling for underdetermined eq", NotImplementedError)
        elif len(unexplained_args) == 0:
            self._raise_or_warn("No handling for already determined eq", NotImplementedError)
        derived_compound = unexplained_args[0]
        parsed_args.remove(derived_compound)

        # solve equation for derived compound
        self._replace_function_with_operators(algebraic_rule=rule)
        try:
            eq = sympy.parse_expr(str(rule.function_body))
            function_body = str(sympy.solve(eq, derived_compound)[0])
        except AttributeError:
            self._raise_or_warn("Equation may not only contain symbols and operators", NotImplementedError)
        except TypeError:
            self._raise_or_warn("Equation may not only contain symbols and operators", NotImplementedError)

        sbml_id = rule.sbml_id
        if sbml_id is None or sbml_id == "":
            sbml_id = derived_compound

        self.derived_compounds.add(derived_compound)
        self.converted_algebraic_modules[rule.sbml_id] = AssignmentRule(
            sbml_id=sbml_id,
            sbml_math=function_body,
            parsed_args=parsed_args,
            compounds=[],
            modifiers=[],
            derived_compound=derived_compound,
            parameters=[],
            function_body=function_body,
            function_args=[],
        )

    def convert_algebraic_rules(self) -> None:
        for rule in self.parsed_algebraic_rules.values():
            self._convert_algebraic_to_assignment_rule(rule=rule)

    def convert_assignment_rules(self) -> None:
        for sbml_id, rule in self.parsed_assignment_rules.items():
            parsed_args = rule.parsed_args
            compounds = [i for i in parsed_args if i in self.converted_variables]
            parameters = [i for i in parsed_args if i in self.converted_constants]
            modifiers = sorted(set(parsed_args).difference(compounds).difference(parameters))
            function_args = compounds + modifiers + parameters

            self.derived_compounds.add(rule.derived_compound)
            self.converted_algebraic_modules[sbml_id] = AssignmentRule(
                sbml_id=sbml_id,
                sbml_math=rule.sbml_math,
                parsed_args=rule.parsed_args,
                compounds=compounds,
                derived_compound=rule.derived_compound,
                modifiers=modifiers,
                parameters=parameters,
                function_body=rule.function_body,
                function_args=function_args,
            )

    def _convert_rate_rule_to_reaction(self, rule: RateRule) -> None:
        derived_compound = rule.derived_compound
        if derived_compound in self.parsed_compartments:
            self._raise_or_warn("Dynamic compartments are unsupported", NotImplementedError)
        parsed_args = rule.parsed_args
        modifiers = rule.modifiers
        if derived_compound in parsed_args:
            modifiers.append(derived_compound)
        compounds = [i for i in parsed_args if i in self.converted_variables]
        parameters = [i for i in parsed_args if i in self.converted_constants]
        modifiers.extend([i for i in compounds if i != derived_compound])
        modifiers = sorted(set(modifiers))

        try:
            species = self.parsed_species[derived_compound]
            if species.has_only_substance_units:
                function_body = rule.function_body
            else:
                compartment = self.parsed_species[derived_compound].compartment
                if compartment is not None:
                    if self.parsed_compartments[compartment].dimensions > 0:
                        if self.parsed_species[derived_compound].is_concentration:
                            function_body = rule.function_body
                        else:
                            function_body = f"({rule.function_body}) * {compartment}"
                            parsed_args.append(compartment)
                    else:
                        function_body = rule.function_body
                else:
                    function_body = rule.function_body
        except KeyError:
            function_body = rule.function_body

        # parsed_reactants = {i: -1 for i in reactants}
        parsed_products = {derived_compound: 1}

        self.converted_reactions[rule.sbml_id] = Reaction(
            sbml_id=rule.sbml_id,
            sbml_math=rule.sbml_math,
            is_reversible=False,
            modifiers=modifiers,
            parsed_args=parsed_args,
            parsed_reactants={},
            parsed_products=parsed_products,
            function_body=function_body,
            function_args=rule.function_args,
            parameters=parameters,
            stoichiometry={},
        )

    def convert_rate_rules(self) -> None:
        for rule_id, rule in self.parsed_rate_rules.items():
            self._convert_rate_rule_to_reaction(rule=rule)

    def convert_reactions(self) -> None:
        self.converted_reactions.update(copy.deepcopy(self.parsed_reactions))

    def convert_initial_assignments(self) -> None:
        for target, assignment in self.parsed_initial_assignments.items():
            if target in self.converted_constants:
                self.converted_derived_constants[target] = assignment
            else:
                self.converted_initial_assignments[target] = assignment

    def _collect_and_convert(self) -> None:
        self.collect_slow_changing_compounds()

        # constants and variables
        self.convert_parameters()
        self.convert_compartments()
        self.convert_compounds()

        # derived parameters and initial assignments
        self.convert_initial_assignments()

        # algebraic modules
        self.convert_algebraic_rules()
        self.convert_assignment_rules()

        # reactions
        self.convert_rate_rules()
        self.convert_reactions()

    ###############################################################################
    # Handling stage
    ###############################################################################

    def handle_functions(self) -> None:
        for sbml_id, function in self.parsed_functions.items():
            function.function_body = _simplify_function_body(function_body=function.function_body)
            self.converted_functions[sbml_id] = function

    def _delete_derived_compounds_from_compounds(self) -> None:
        for compound in self.derived_compounds:
            if compound in self.converted_variables:
                del self.converted_variables[compound]

    def _sort_assignment_rules(self) -> None:
        """Make sure that dependencies on other assignment rules are
        calculated in order"""
        unsorted_modules = self.converted_algebraic_modules.copy()
        available_compounds = set(self.converted_variables)
        required_compounds = {k: set(v.compounds) for k, v in unsorted_modules.items()}

        sorted_modules = {}
        while True:
            modules_to_change = []
            for module_id, module in unsorted_modules.items():
                if required_compounds[module_id].issubset(available_compounds):
                    modules_to_change.append(module_id)

            for module_id in modules_to_change:
                module = unsorted_modules.pop(module_id)
                available_compounds.add(module.derived_compound)
                sorted_modules[module_id] = module

            if len(modules_to_change) == 0:
                break
            if len(unsorted_modules) == 0:
                break

        self.converted_algebraic_modules = sorted_modules

    def _set_module_func_args(self, module: AssignmentRule) -> None:
        parsed_args = module.parsed_args
        compounds = [i for i in parsed_args if i in self.converted_variables]
        parameters = [i for i in parsed_args if i in self.converted_constants]
        modifiers = set(module.modifiers).difference(parameters)

        unexplained_args = set(parsed_args).difference(compounds).difference(parameters)
        modifiers_ = cast(List[str], sorted(set(modifiers).union(unexplained_args)))

        module.function_args = compounds + modifiers_ + parameters
        module.compounds = compounds
        module.parameters = parameters
        module.modifiers = modifiers_

    def handle_algebraic_modules(self) -> None:
        self._delete_derived_compounds_from_compounds()
        for module in self.converted_algebraic_modules.values():
            # watch out for species reference
            derived_compound = module.derived_compound
            if "ref" in derived_compound:
                if derived_compound.rsplit("ref", maxsplit=1)[0] in self.parsed_species:
                    self._raise_or_warn("Dynamic stoichiometries not supported", NotImplementedError)

            self._set_module_func_args(module=module)
            module.function_body = _simplify_function_body(function_body=module.function_body)
        self._sort_assignment_rules()

    def _set_reaction_stoichiometries(self, reaction: Reaction) -> None:
        """Exclude compounds that are actually parameters"""
        stoichiometry: Dict[str, float] = {}
        modifiers = reaction.modifiers
        for substrate, value in reaction.parsed_reactants.items():
            if substrate in self.converted_variables:
                if substrate in self.derived_compounds:
                    modifiers.append(substrate)
                else:
                    stoichiometry[substrate] = stoichiometry.get(substrate, 0) + value
        for product, value in reaction.parsed_products.items():
            if product in self.converted_variables:
                if product in self.derived_compounds:
                    modifiers.append(product)
                else:
                    stoichiometry[product] = stoichiometry.get(product, 0) + value
        reaction.stoichiometry = stoichiometry
        reaction.modifiers = sorted(set(modifiers))

    def _convert_substance_amount_to_concentration(self, reaction: Reaction) -> None:
        """Convert mole to mole / l
        The compounds in the test are supplied in mole if has_only_substance_units is false
        In that case, the reaction equation has to be reformed like this
        k1 * S1 * compartment -> k1 * S1
        or in other words the species have to be divided by the compartment to get
        concentration units
        """
        function_body = reaction.function_body
        removed_compartments = set()
        for arg in reaction.parsed_args:
            # the parsed species part is important to not
            # introduce conversion on things that aren't species
            species = self.parsed_species.get(arg, None)
            if species is None:
                continue
            if not species.has_only_substance_units:
                sbml_id = species.sbml_id
                compartment = species.compartment
                if compartment is not None:
                    if self.parsed_compartments[compartment].dimensions == 0:
                        continue
                    if species.is_concentration:
                        if compartment not in removed_compartments:
                            pattern = f"({compartment})" + r"\b"
                            repl = f"({compartment} / {compartment})"
                            function_body = re.sub(pattern, repl, function_body)
                            removed_compartments.add(compartment)
                    else:
                        pattern = f"({sbml_id})" + r"\b"
                        repl = f"({sbml_id} / {compartment})"
                        function_body = re.sub(pattern, repl, function_body)
                    if compartment not in reaction.parsed_args:
                        reaction.parsed_args.append(compartment)
        reaction.function_body = function_body

    def _set_reaction_func_args(self, reaction: Reaction) -> None:
        all_parameters = set(self.converted_constants)
        parsed_args = reaction.parsed_args
        # remove unused (simplify after convert to concentration)
        parsed_args = [i for i in parsed_args if i in reaction.function_body]
        stoichiometry = reaction.stoichiometry
        substrates = [k for k, v in stoichiometry.items() if v < 0]
        parameters = [i for i in parsed_args if i in all_parameters]
        modifiers = set(reaction.modifiers).difference(parameters)

        if reaction.is_reversible:
            products = [k for k, v in stoichiometry.items() if v > 0]
            compound_args = substrates + products
        else:
            compound_args = substrates

        unexplained_args = set(parsed_args).difference(parameters).difference(compound_args)
        modifiers_ = sorted(set(modifiers).union(unexplained_args))
        reaction.function_args = compound_args + modifiers_ + parameters
        reaction.parameters = parameters
        reaction.modifiers = modifiers_

    def handle_reactions(self) -> None:
        for sbml_id, reaction in self.converted_reactions.items():
            self._set_reaction_stoichiometries(reaction=reaction)
            self._convert_substance_amount_to_concentration(reaction=reaction)
            reaction.function_body = _simplify_function_body(function_body=reaction.function_body)
            self._set_reaction_func_args(reaction=reaction)

    def handle_initial_assignments(self) -> None:
        for assignment in self.converted_initial_assignments.values():
            derived_parameter = assignment.derived_parameter
            if derived_parameter in self.parsed_species:
                species = self.parsed_species[derived_parameter]
                if species.is_concentration:
                    continue
                compartment = self.parsed_species[derived_parameter].compartment
                if compartment is not None:
                    if self.parsed_compartments[compartment].dimensions == 0:
                        continue
                    function_body = assignment.function_body
                    if compartment not in function_body:
                        assignment.function_body = f"({function_body}) * {compartment}"
                        assignment.function_args.append(compartment)

    def _handle(self) -> None:
        self.handle_functions()
        self.handle_algebraic_modules()
        self.handle_reactions()
        self.handle_initial_assignments()

    ###############################################################################
    # Building stage
    ###############################################################################

    @staticmethod
    def create_python_function(
        func: Union[InitialAssignment, AssignmentRule, Reaction, Function]
    ) -> Callable:
        """Create and exec function"""
        func_name = func.sbml_id
        func_args = ", ".join(func.function_args)
        func_body = func.function_body
        func_str = "\n".join(
            [
                f"def {func_name}({func_args}) -> None:",
                f"{INDENT}return {func_body}",
                "",
            ]
        )
        try:
            exec(func_str, globals(), None)
        except SyntaxError as e:
            raise SyntaxError(f"Invalid function definition: {func_str}") from e
        python_func = globals()[func.sbml_id]
        python_func.__source__ = func_str
        return python_func  # type: ignore

    def build_model_from_sbml(self) -> Tuple[Model, Dict[str, Any]]:
        # Do the parsing
        self._parse()
        self._collect_and_convert()
        self._handle()

        model = Model(
            meta_info={
                "id": self.sbml_model.getId(),
                "name": self.sbml_model.getName(),
                # "compartments": self.compartments,
                # "units": self.units,
            }
        )
        for func_name, func in self.converted_functions.items():
            model.add_function(
                function_name=func_name,
                function=self.create_python_function(func=func),
            )

        # Parameters
        constants = {k: v.value for k, v in self.converted_constants.items()}
        model.add_parameters(parameters=constants)

        # Derived parameters
        for par_name, assignment in self.converted_derived_constants.items():
            try:
                model.remove_parameter(parameter_name=par_name)
            except KeyError:
                pass
            try:
                model.add_derived_parameter(
                    parameter_name=par_name,
                    function=self.create_python_function(func=assignment),
                    parameters=assignment.function_args,
                )
            except KeyError:
                self._raise_or_warn(
                    "Cannot use non-parameter inputs for derived parameter", NotImplementedError
                )

        # Compounds
        model.add_compounds(sorted(set(self.converted_variables)))

        # Algebraic modules
        for module_name, module in self.converted_algebraic_modules.items():
            model.add_algebraic_module(
                module_name=module_name,
                function=self.create_python_function(func=module),
                compounds=module.compounds,
                derived_compounds=[module.derived_compound],
                modifiers=module.modifiers,
                parameters=module.parameters,
            )

        # Reactions
        for reaction_id, reaction in self.converted_reactions.items():
            meta_info = {
                "sbml_function": reaction.sbml_math,
                "python_function": reaction.function_body,
            }
            model.add_reaction(
                rate_name=reaction_id,
                function=self.create_python_function(func=reaction),
                stoichiometry=reaction.stoichiometry,
                modifiers=reaction.modifiers,
                parameters=reaction.parameters,
                reversible=reaction.is_reversible,
                **meta_info,  # type: ignore
            )

        y0 = []
        for i in self.converted_variables.values():
            initial_amount = i.initial_amount
            if i.has_only_substance_units:
                if i.is_concentration:
                    if i.compartment is not None:
                        initial_amount *= self.parsed_compartments[i.compartment].size
            y0.append(initial_amount)
        y0_arr = np.array(y0)
        y0_arr[np.isnan(y0)] = 0
        y0_dict = dict(zip(self.converted_variables, y0))

        # Initial assignments
        possible_sources: Dict[str, Any] = {**model.get_full_concentration_dict(y0), **model.parameters}
        for par_name, assignment in self.converted_initial_assignments.items():
            py_func = self.create_python_function(func=assignment)
            res = py_func(*[possible_sources[k] for k in assignment.function_args])
            if isinstance(res, (list, np.ndarray)):
                res = res[0]
            if par_name not in model.compounds and par_name not in model.get_derived_compounds():
                self._raise_or_warn("Initial assignment targeting unknown type", NotImplementedError)
            y0_dict[par_name] = res
        return model, y0_dict
