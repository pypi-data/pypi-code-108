"""
Tools for organizing the graph documentation.
"""

from dataclasses import dataclass
from enum import (
    Enum,
    auto,
)
from typing import (
    Dict,
    List,
)


@dataclass
class DocumentationSection:
    """
    A section of the graphs documentation.

    Parameters
    ----------
    title : str
        The title of the section.
    description : str
        The description of the section.
    operations : str
        The names of the operations to be listed in the section.
    subsections : list[DocumentationSection]
        The subsections that should be nested inside the section.
    """

    title: str
    description: str
    operations: List[str]
    subsections: List["DocumentationSection"]


class Category(Enum):
    """
    The different categories of graph operations.
    """

    ARITHMETIC_FUNCTIONS = auto()
    BASIC_FUNCTIONS = auto()
    BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS = auto()
    BUILDING_SMOOTH_HAMILTONIANS = auto()
    COMPLEX_NUMBERS = auto()
    DEPRECATED_OPERATIONS = auto()
    DERIVATIVES = auto()
    FILTERING_AND_DISCRETIZING = auto()
    HYPERBOLIC_FUNCTIONS = auto()
    LARGE_SYSTEMS = auto()
    LINEAR_ALGEBRA = auto()
    MANIPULATING_TENSORS = auto()
    MOLMER_SORENSEN = auto()
    OPTIMAL_AND_ROBUST_CONTROL = auto()
    OPTIMIZATION_VARIABLES = auto()
    OTHER_OPERATIONS = auto()
    RANDOM_OPERATIONS = auto()
    TIME_EVOLUTION = auto()
    TRIGONOMETRIC_FUNCTIONS = auto()


def create_documentation_sections(
    operations: Dict[str, List[Category]]
) -> List[DocumentationSection]:
    """
    Creates sections containing the full operations documentation.

    Parameters
    ----------
    operations : dict[str, list[Category]]
        The operations and their associated categories.

    Returns
    -------
    list[DocumentationSection]
        A list of objects describing the top-level operations documentation sections. Each category
        appears exactly once in the nested structure of sections.
    """
    categories_map: Dict[Category, List[str]] = {category: [] for category in Category}

    for name, categories in sorted(operations.items()):
        for category in categories:
            categories_map[category].append(name)

    sections = [
        DocumentationSection(
            "Optimization variables",
            "When performing optimizations, you can use these operations to create the optimizable "
            "variables that can be tuned by the optimizer in order to minimize your cost function.",
            categories_map.pop(Category.OPTIMIZATION_VARIABLES),
            [],
        ),
        DocumentationSection(
            "Building Hamiltonians",
            "You can use these operations to build graphs representing Hamiltonians. Hamiltonians "
            "are represented as tensor-valued functions of time. Tensor-valued functions of time "
            "can be either piecewise-constant (PWCs) or smooth (STFs, which stands for sampleable "
            "tensor functions). You can manipulate PWCs and STFs either by using the operations in "
            "this section or by applying most "
            ":ref:`mathematical functions <Mathematical functions>`. You can also convert PWCs "
            "into STFs by applying linear filters, and can convert STFs into PWCs by discretizing.",
            [],
            [
                DocumentationSection(
                    "Working with piecewise-constant tensor functions (PWCs)",
                    "",
                    categories_map.pop(
                        Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS
                    ),
                    [],
                ),
                DocumentationSection(
                    "Working with sampleable tensor functions (STFs)",
                    "You can use these functions to create and manipulate STFs. Note that a "
                    "powerful way to create analytic STFs is to start with "
                    ":py:obj:`~Graph.identity_stf` and then apply a sequence of "
                    ":ref:`mathematical functions <Mathematical functions>`.",
                    categories_map.pop(Category.BUILDING_SMOOTH_HAMILTONIANS),
                    [],
                ),
                DocumentationSection(
                    "Filtering and discretizing",
                    "",
                    categories_map.pop(Category.FILTERING_AND_DISCRETIZING),
                    [],
                ),
            ],
        ),
        DocumentationSection(
            "Time evolution",
            "You can use these operations to calculate the time evolution of your open or closed "
            "quantum system, either for simulations or optimizations.",
            categories_map.pop(Category.TIME_EVOLUTION),
            [],
        ),
        DocumentationSection(
            "Optimal and robust control",
            "You can use these operations, together with the operations for creating "
            ":ref:`optimization variables<Optimization variables>` and "
            ":ref:`Hamiltonians <Building Hamiltonians>`, "
            "to define convenient cost functions for optimal and robust control.",
            categories_map.pop(Category.OPTIMAL_AND_ROBUST_CONTROL),
            [],
        ),
        DocumentationSection(
            "Large systems",
            "You can use these operations, together with those for building "
            ":ref:`Hamiltonians <Building Hamiltonians>`, to build graphs that efficiently handle "
            "large quantum systems.",
            categories_map.pop(Category.LARGE_SYSTEMS),
            [],
        ),
        DocumentationSection(
            "Mølmer–Sørensen gates",
            "You can use these operations to efficiently model systems described by "
            "Mølmer–Sørensen interactions.",
            categories_map.pop(Category.MOLMER_SORENSEN),
            [],
        ),
        DocumentationSection(
            "Random operations",
            "You can use these operations to create random quantities, which take different values "
            "each time they are evaluated. These operations are most useful in simulations and "
            "stochastic optimizations.",
            categories_map.pop(Category.RANDOM_OPERATIONS),
            [],
        ),
        DocumentationSection(
            "Manipulating tensors",
            "You can use these operations to manipulate the structures of tensors.",
            categories_map.pop(Category.MANIPULATING_TENSORS),
            [],
        ),
        DocumentationSection(
            "Mathematical functions",
            "You can use these operations to perform standard mathematical computations.",
            [],
            [
                DocumentationSection(
                    "Arithmetic",
                    "",
                    categories_map.pop(Category.ARITHMETIC_FUNCTIONS),
                    [],
                ),
                DocumentationSection(
                    "Linear algebra",
                    "",
                    categories_map.pop(Category.LINEAR_ALGEBRA),
                    [],
                ),
                DocumentationSection(
                    "Basic functions",
                    "",
                    categories_map.pop(Category.BASIC_FUNCTIONS),
                    [],
                ),
                DocumentationSection(
                    "Trigonometric functions",
                    "",
                    categories_map.pop(Category.TRIGONOMETRIC_FUNCTIONS),
                    [],
                ),
                DocumentationSection(
                    "Hyperbolic functions",
                    "",
                    categories_map.pop(Category.HYPERBOLIC_FUNCTIONS),
                    [],
                ),
                DocumentationSection(
                    "Handling complex numbers",
                    "",
                    categories_map.pop(Category.COMPLEX_NUMBERS),
                    [],
                ),
                DocumentationSection(
                    "Derivatives",
                    "",
                    categories_map.pop(Category.DERIVATIVES),
                    [],
                ),
            ],
        ),
        DocumentationSection(
            "Other operations",
            "You typically do not need to use these operations directly.",
            categories_map.pop(Category.OTHER_OPERATIONS),
            [],
        ),
        DocumentationSection(
            "Deprecated operations",
            "These operations are deprecated and will be removed in the future.",
            categories_map.pop(Category.DEPRECATED_OPERATIONS),
            [],
        ),
    ]
    # Verify that we dealt with all the categories.
    assert not categories_map
    return sections
