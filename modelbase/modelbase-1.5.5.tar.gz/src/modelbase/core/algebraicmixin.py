from __future__ import annotations

__all__ = [
    "Module",
    "AlgebraicModule",
]

import copy
import warnings
from dataclasses import dataclass, field
from queue import Empty, SimpleQueue
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import libsbml
import numpy as np
import numpy.typing as npt

from .basemodel import BaseModel
from .compoundmixin import CompoundMixin
from .parametermixin import ParameterMixin
from .utils import (
    check_function_arity,
    get_formatted_function_source_code,
    patch_lambda_function_name,
    warning_on_one_line,
)

warnings.formatwarning = warning_on_one_line  # type: ignore


@dataclass
class Module:
    """Meta-info container for an algebraic module."""

    common_name: Optional[str] = None
    notes: dict = field(default_factory=dict)
    database_links: dict = field(default_factory=dict)


class AlgebraicModule:
    """Container for algebraic modules"""

    def __init__(
        self,
        name: str,
        function: Union[Callable[..., float], Callable[..., Iterable[float]]],
        derived_compounds: List[str],
        compounds: List[str],
        modifiers: List[str],
        parameters: List[str],
        dynamic_variables: List[str],
        args: List[str],
    ):
        self.name = name
        self.function = function
        self.compounds = compounds
        self.derived_compounds = derived_compounds
        self.modifiers = modifiers
        self.parameters = parameters
        self.dynamic_variables = dynamic_variables
        self.args = args

    def check_consistency(self) -> None:
        """Check whether all arguments exists and the arity matches"""
        self._check_dynamic_variables()
        self._check_module_args()

        if not check_function_arity(function=self.function, arity=len(self.args)):
            warnings.warn(f"Function arity does not match args of {self.name}")

    def _check_dynamic_variables(self) -> None:
        difference = set(self.dynamic_variables).difference(self.compounds + self.modifiers)
        if difference:
            warnings.warn(
                f"Supplied args {difference} for module {self.name} that aren't in compounds or modifiers"
            )

    def _check_module_args(self) -> None:
        difference = set(self.args).difference(self.dynamic_variables + self.parameters)
        if difference:
            warnings.warn(
                f"Supplied args {difference} for module {self.name} that aren't in compounds, modifiers or parameters"
            )

    def __repr__(self) -> str:
        return repr(self.__dict__)

    def __str__(self) -> str:
        return f"{self.function.__name__}({', '.join(self.args)}) -> {self.derived_compounds}"

    def keys(self) -> List[str]:
        """Get all valid keys of the algebraic module"""
        return [
            "function",
            "compounds",
            "derived_compounds",
            "modifiers",
            "parameters",
            "dynamic_variables",
            "args",
        ]

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __iter__(self) -> Generator:
        yield "function", self.function
        yield "compounds", self.compounds
        yield "derived_compounds", self.derived_compounds
        yield "modifiers", self.modifiers
        yield "parameters", self.parameters
        yield "dynamic_variables", self.dynamic_variables
        yield "args", self.args

    def copy(self) -> AlgebraicModule:
        """Create a copy of the module"""
        return copy.deepcopy(self)


class AlgebraicMixin(ParameterMixin, CompoundMixin, BaseModel):
    """Mixin for algebraic modules.

    This adds the capability to calculate concentrations of derived
    compounds that are calculated before the rate functions are calculated.
    """

    def __init__(self, algebraic_modules: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        self.algebraic_modules: Dict[str, AlgebraicModule] = {}
        self._algebraic_module_order: List[str] = []
        if algebraic_modules is not None:
            self.add_algebraic_modules(algebraic_modules=algebraic_modules)

    ##########################################################################
    # Derived compound functions
    ##########################################################################

    def get_derived_compounds(self) -> List[str]:
        """Return names of compounds derived from algebraic modules."""
        derived_compounds = []
        for module in self.algebraic_modules.values():
            derived_compounds.extend(module.derived_compounds)
        return derived_compounds

    @property
    def derived_compounds(self) -> List[str]:
        """Return names of compounds derived from algebraic modules

        Used to be an attribute of the model, so this is kept to ensure backwards compatability
        """
        return self.get_derived_compounds()

    def _get_all_compounds(self) -> List[str]:
        return list(self.get_compounds() + self.get_derived_compounds())

    def get_all_compounds(self) -> List[str]:
        """Return names of compounds and derived compounds (in that order)."""
        return self._get_all_compounds()

    ##########################################################################
    # Algebraic Modules
    ##########################################################################

    def _sort_algebraic_modules(self, max_iterations: int = 10_000) -> None:
        def submodule(v: AlgebraicModule) -> Dict[str, Set[str]]:
            return {
                "in": set(v.compounds),
                "out": set(v.derived_compounds),
            }

        available_compounds = set(self.compounds)
        module_order = []
        modules_to_sort: SimpleQueue = SimpleQueue()
        for k, v in self.algebraic_modules.items():
            modules_to_sort.put((k, submodule(v)))

        last_name = None
        i = 0
        while True:
            try:
                name, mod = modules_to_sort.get_nowait()
            except Empty:
                break
            if mod["in"].issubset(available_compounds):
                available_compounds.update(mod["out"])
                module_order.append(name)
            else:
                if last_name == name:
                    module_order.append(name)
                    break
                modules_to_sort.put((name, mod))
                last_name = name
            i += 1
            if i > max_iterations:
                raise ValueError(
                    "Exceeded max iterations on algebraic module sorting. Check if there are circular references."
                )
        self._algebraic_module_order = module_order

    def _check_module_consistency(self, module: AlgebraicModule, check_ids: bool = True) -> None:
        self._check_for_existence(
            name=module.name,
            check_against=self.get_all_compounds(),
            candidates=module.compounds + module.modifiers,
            element_type="compound",
            raise_on_missing=False,
        )
        self._check_for_existence(
            name=module.name,
            check_against=self.get_parameter_names(),
            candidates=module.parameters,
            element_type="parameter",
        )
        if check_ids:
            self._check_and_insert_ids(module.derived_compounds, context=module.name)
        module.check_consistency()

    def add_algebraic_module(
        self,
        module_name: str,
        function: Union[Callable[..., float], Callable[..., Iterable[float]]],
        compounds: List[str] = None,
        derived_compounds: List[str] = None,
        modifiers: List[str] = None,
        parameters: List[str] = None,
        dynamic_variables: List[str] = None,
        args: List[str] = None,
        check_consistency: bool = True,
        sort_modules: bool = True,
        **meta_info: Dict[str, Any],
    ) -> None:
        """Add an algebraic module to the model.

        CAUTION: The Python function of the module has to return an iterable.
        The Python function will get the function arguments in the following order:
        [**compounds, **modifiers, **parameters]

        Warns
        -----
        UserWarning
            If algebraic module is already in the model.

        Examples
        --------
        def rapid_equilibrium(substrate, k_eq)-> None:
            x = substrate / (1 + k_eq)
            y = substrate * k_eq / (1 + k_eq)
            return x, y

        add_algebraic_module(
            module_name="fast_eq",
            function=rapid_equilibrium,
            compounds=["A"],
            derived_compounds=["X", "Y"],
            parameters=["K"],
        )
        """
        if module_name in self.algebraic_modules:
            self.remove_algebraic_module(module_name=module_name)
            warnings.warn(f"Overwriting algebraic module {module_name}")

        patch_lambda_function_name(function=function, name=module_name)

        if compounds is None:
            compounds = []
        if derived_compounds is None:
            derived_compounds = []
        if modifiers is None:
            modifiers = []
        if parameters is None:
            parameters = []
        if dynamic_variables is None:
            dynamic_variables = compounds + modifiers
        if args is None:
            args = dynamic_variables + parameters

        module = AlgebraicModule(
            name=module_name,
            function=function,
            compounds=compounds,
            derived_compounds=derived_compounds,
            modifiers=modifiers,
            parameters=parameters,
            dynamic_variables=dynamic_variables,
            args=args,
        )
        self.algebraic_modules[module_name] = module

        self.meta_info.setdefault("modules", {}).setdefault(
            module_name,
            Module(**meta_info),  # type: ignore
        )

        if check_consistency:
            self._check_module_consistency(module)
        if sort_modules:
            self._sort_algebraic_modules()

    def add_algebraic_modules(self, algebraic_modules: dict, meta_info: dict = None) -> None:
        """Add multiple algebraic modules to the model.

        See Also
        --------
        add_algebraic_module
        """
        meta_info = {} if meta_info is None else meta_info
        for module_name, module in algebraic_modules.items():
            info = meta_info.get(module_name, {})
            self.add_algebraic_module(module_name=module_name, **module, **info)

    def update_algebraic_module(
        self,
        module_name: str,
        function: Union[Callable[..., float], Callable[..., Iterable[float]]] = None,
        compounds: List[str] = None,
        derived_compounds: List[str] = None,
        modifiers: List[str] = None,
        parameters: List[str] = None,
        dynamic_variables: List[str] = None,
        args: List[str] = None,
        check_consistency: bool = True,
        sort_modules: bool = True,
    ) -> None:
        """Update an existing reaction."""
        module = self.algebraic_modules[module_name]
        args_have_changed = False
        derived_have_changed = False

        if function is not None:
            patch_lambda_function_name(function=function, name=module_name)
            module.function = function

        if compounds is not None:
            module.compounds = compounds
            args_have_changed = True
        else:
            compounds = module.compounds

        if derived_compounds is not None:
            self._remove_ids(module.derived_compounds)
            module.derived_compounds = derived_compounds
            derived_have_changed = True

        if modifiers is not None:
            module.modifiers = modifiers
            args_have_changed = True
        else:
            modifiers = module.modifiers

        if parameters is not None:
            module.parameters = parameters
            args_have_changed = True
        else:
            parameters = module.parameters

        if dynamic_variables is not None:
            args_have_changed = True
            module.dynamic_variables = dynamic_variables
        elif args_have_changed:
            dynamic_variables = compounds + modifiers
            module.dynamic_variables = dynamic_variables
        else:
            dynamic_variables = module.dynamic_variables

        if args is not None:
            dynamic_variables = [i for i in args if i in module.dynamic_variables]
            module.dynamic_variables = dynamic_variables
            module.args = args
        elif args_have_changed:
            args = dynamic_variables + parameters
            module.args = args
        else:
            args = module.args

        if check_consistency:
            self._check_module_consistency(module, check_ids=derived_have_changed)
        if sort_modules:
            self._sort_algebraic_modules()

    def update_algebraic_modules(self, modules: dict) -> None:
        """Update multiple algebraic modules

        See Also
        --------
        update_algebraic_module
        """
        for name, module in modules.items():
            self.update_algebraic_module(name, **module)

    def update_module_meta_info(self, module: str, meta_info: dict) -> None:
        """Update meta info of an algebraic module.

        Parameters
        ----------
        module : str
            Name of the algebraic module
        meta_info : dict
            Meta info of the algebraic module. Allowed keys are
            {common_name, notes, database_links}
        """
        self.update_meta_info(component="modules", meta_info={module: meta_info})

    def remove_algebraic_module(self, module_name: str, sort_modules: bool = True) -> None:
        """Remove an algebraic module.

        Parameters
        ----------
        module_name : str
            Name of the algebraic module
        """
        module = self.algebraic_modules.pop(module_name)
        self._remove_ids(module.derived_compounds)
        if sort_modules:
            self._sort_algebraic_modules()

    def remove_algebraic_modules(self, module_names: List[str]) -> None:
        """Remove multiple algebraic modules.

        Parameters
        ----------
        module_names : iterable(str)
            Names of the algebraic modules
        """
        for module_name in module_names:
            self.remove_algebraic_module(module_name=module_name)

    def get_algebraic_module(self, module_name: str) -> AlgebraicModule:
        """Return the algebraic module"""
        return self.algebraic_modules[module_name]

    def get_algebraic_module_function(
        self, module_name: str
    ) -> Union[Callable[..., float], Callable[..., Iterable[float]]]:
        """Return the function of the algebraic module"""
        return self.algebraic_modules[module_name].function

    def get_algebraic_module_compounds(self, module_name: str) -> List[str]:
        """Return the compounds of the algebraic module"""
        return list(self.algebraic_modules[module_name].compounds)

    def get_algebraic_module_derived_compounds(self, module_name: str) -> List[str]:
        """Return the derived compounds of the algebraic module"""
        return list(self.algebraic_modules[module_name].derived_compounds)

    def get_algebraic_module_modifiers(self, module_name: str) -> List[str]:
        """Return the modifiers of the algebraic module"""
        return list(self.algebraic_modules[module_name].modifiers)

    def get_algebraic_module_parameters(self, module_name: str) -> List[str]:
        """Return the parameters of the algebraic module"""
        return list(self.algebraic_modules[module_name].parameters)

    def get_algebraic_module_args(self, module_name: str) -> List[str]:
        """Return the arguments of the algebraic module function"""
        return list(self.algebraic_modules[module_name].args)

    ##########################################################################
    # Simulation functions
    ##########################################################################

    def _get_fcd(
        self,
        *,
        t: npt.NDArray[np.float64],
        y: Dict[str, npt.NDArray[np.float64]],
    ) -> Dict[str, npt.NDArray[np.float64]]:
        """Calculate the derived variables of all algebraic modules.

        fdc = full_concentration_dict

        The derived compounds are sorted by the algebraic modules and their internal
        derived_modules attribute.
        """
        y["time"] = t
        # args = self.parameters | y # that is python 3.9+ syntax, wait for a bit
        args: Dict[str, Union[float, npt.NDArray[np.float64]]] = {**self.parameters, **y}
        for name, module in self.algebraic_modules.items():
            try:
                derived_values = module.function(*(args[arg] for arg in module.args))
            except KeyError as e:
                raise KeyError(f"Could not find argument {e} for module {name}") from e
            derived_compounds = dict(
                zip(
                    module.derived_compounds,
                    np.array(derived_values).reshape((len(module.derived_compounds), -1)),
                )
            )
            y.update(derived_compounds)
            args.update(derived_compounds)
        return y

    ##########################################################################
    # Source code functions
    ##########################################################################

    def _generate_algebraic_modules_source_code(self, *, include_meta_info: bool = True) -> Tuple[str, str]:
        """Generate modelbase source code for algebraic modules.

        This is mainly used for the generate_model_source_code function.

        Parameters
        ----------
        include_meta_info : bool
            Whether to include meta info in the source code.

        Returns
        -------
        algebraic_module_source_code : str
            Code generating the Python functions of the algebraic modules
        algebraic_module_modelbase_code : str
            Code generating the modelbase objects

        See Also
        --------
        generate_model_source_code
        """
        module_functions = set()
        modules = []
        for name, module in self.algebraic_modules.items():
            function = module.function
            compounds = module.compounds
            derived_compounds = module.derived_compounds
            modifiers = module.modifiers
            parameters = module.parameters
            args = module.args

            function_code = get_formatted_function_source_code(
                function_name=name, function=function, function_type="module"
            )
            module_functions.add(function_code)
            module_definition = (
                "m.add_algebraic_module(\n"
                f"    module_name={repr(name)},\n"
                f"    function={function.__name__},\n"
                f"    compounds={compounds},\n"
                f"    derived_compounds={derived_compounds},\n"
                f"    modifiers={modifiers},\n"
                f"    parameters={parameters},\n"
                f"    args={args},\n"
            )
            if include_meta_info:
                meta_info = self._get_nonzero_meta_info(component="modules")
                try:
                    info = meta_info[name]
                    module_definition += f"**{info}"
                except KeyError:
                    pass
            module_definition += ")"
            modules.append(module_definition)
        return "\n".join(sorted(module_functions)), "\n".join(modules)

    ##########################################################################
    # SBML functions
    ##########################################################################

    def _create_sbml_algebraic_modules(self, *, _sbml_model: libsbml.Model) -> None:
        """Convert the algebraic modules their sbml equivalent.

        Notes
        -----
        The closest we can get in SBML are assignment rules of the form x = f(V), see
        http://sbml.org/Software/libSBML/docs/python-api/classlibsbml_1_1_assignment_rule.html

        Thus we have to split algebraic modules that contain multiple derived compounds
        into multiple assignment rules.

        But apparently they do not support parameters, so for now I am skipping
        this.
        """
        warnings.warn("SBML does support algebraic modules, skipping.")
