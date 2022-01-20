from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union
from momotor.bundles.binding.xml import LangValue

__NAMESPACE__ = "http://momotor.org/1.0"


@dataclass
class DependsComplexType:
    class Meta:
        name = "dependsComplexType"

    step: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class FileComplexType:
    class Meta:
        name = "fileComplexType"

    any_element: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    ref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    class_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "class",
            "type": "Attribute",
        }
    )
    src: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    encoding: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    any_attributes: Dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##any",
        }
    )


@dataclass
class LinkComplexType:
    class Meta:
        name = "linkComplexType"

    src: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class OptionComplexType:
    class Meta:
        name = "optionComplexType"

    any_element: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    ref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    domain: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    description: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    encoding: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    any_attributes: Dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##any",
        }
    )


class OutcomeSimpleType(Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


class PropertyComplexTypeAccept(Enum):
    EQ = "eq"
    NE = "ne"
    LT = "lt"
    LE = "le"
    GT = "gt"
    GE = "ge"
    ONE_OF = "one-of"
    IN_RANGE = "in-range"
    ANY = "any"
    NONE = "none"


@dataclass
class ResourceComplexType:
    class Meta:
        name = "resourceComplexType"

    any_element: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


class StepComplexTypePriority(Enum):
    MUST_PASS = "must-pass"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    DEFAULT = "default"


@dataclass
class DependenciesComplexType:
    class Meta:
        name = "dependenciesComplexType"

    depends: List[DependsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )


@dataclass
class FilesComplexType:
    class Meta:
        name = "filesComplexType"

    file: List[FileComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    baseclass: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    basename: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    basesrc: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class MetaComplexType:
    class Meta:
        name = "metaComplexType"

    name: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    version: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    author: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    description: List["MetaComplexType.Description"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    source: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    generator: List[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )

    @dataclass
    class Description:
        any_element: List[object] = field(
            default_factory=list,
            metadata={
                "type": "Wildcard",
                "namespace": "##any",
                "mixed": True,
            }
        )
        lang: Optional[Union[str, LangValue]] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": "http://www.w3.org/XML/1998/namespace",
            }
        )
        base: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )
        type: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )
        encoding: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )
        other_attributes: Dict[str, str] = field(
            default_factory=dict,
            metadata={
                "type": "Attributes",
                "namespace": "##other",
            }
        )


@dataclass
class OptionsComplexType:
    class Meta:
        name = "optionsComplexType"

    option: List[OptionComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    domain: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class PropertyComplexType:
    class Meta:
        name = "propertyComplexType"

    any_element: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    accept: Optional[PropertyComplexTypeAccept] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    type: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    encoding: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    any_attributes: Dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##any",
        }
    )


@dataclass
class ResourcesComplexType:
    class Meta:
        name = "resourcesComplexType"

    resource: List[ResourceComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )


@dataclass
class CheckletComplexType:
    class Meta:
        name = "checkletComplexType"

    repository: List["CheckletComplexType.Repository"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    link: List[LinkComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    index: List[LinkComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    package_version: List["CheckletComplexType.PackageVersion"] = field(
        default_factory=list,
        metadata={
            "name": "package-version",
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    resources: List[ResourcesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    ref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    extras: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    version: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    entrypoint: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )

    @dataclass
    class Repository:
        src: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )
        type: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )
        revision: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )

    @dataclass
    class PackageVersion:
        name: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )
        version: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )


@dataclass
class ConfigComplexType:
    class Meta:
        name = "configComplexType"

    meta: List[MetaComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    options: List[OptionsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    files: List[FilesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class PropertiesComplexType:
    class Meta:
        name = "propertiesComplexType"

    property: List[PropertyComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )


@dataclass
class CheckletsComplexType:
    class Meta:
        name = "checkletsComplexType"

    checklet: List[CheckletComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    basename: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class Config(ConfigComplexType):
    class Meta:
        name = "config"
        namespace = "http://momotor.org/1.0"


@dataclass
class ExpectComplexType:
    class Meta:
        name = "expectComplexType"

    properties: List[PropertiesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    files: List[FilesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    ref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    step: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    outcome: Optional[OutcomeSimpleType] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class ProductComplexType:
    class Meta:
        name = "productComplexType"

    meta: List[MetaComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    options: List[OptionsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    properties: List[PropertiesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    files: List[FilesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class ResultComplexType:
    class Meta:
        name = "resultComplexType"

    checklet: List[CheckletComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    properties: List[PropertiesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    options: List[OptionsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    files: List[FilesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    step: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    outcome: Optional[OutcomeSimpleType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class StepComplexType:
    class Meta:
        name = "stepComplexType"

    meta: List[MetaComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    dependencies: List[DependenciesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    checklet: List[CheckletComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    resources: List[ResourcesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    options: List[OptionsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    files: List[FilesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    ref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    priority: StepComplexTypePriority = field(
        default=StepComplexTypePriority.DEFAULT,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class ExpectedResultComplexType:
    class Meta:
        name = "expectedResultComplexType"

    expect: List[ExpectComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    ref: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class Product(ProductComplexType):
    class Meta:
        name = "product"
        namespace = "http://momotor.org/1.0"


@dataclass
class Result(ResultComplexType):
    class Meta:
        name = "result"
        namespace = "http://momotor.org/1.0"


@dataclass
class ResultsComplexType:
    class Meta:
        name = "resultsComplexType"

    meta: List[MetaComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    checklets: List[CheckletsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    result: List[ResultComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class StepsComplexType:
    class Meta:
        name = "stepsComplexType"

    step: List[StepComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    options: List[OptionsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    checklets: List[CheckletsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )


@dataclass
class Results(ResultsComplexType):
    class Meta:
        name = "results"
        namespace = "http://momotor.org/1.0"


@dataclass
class TestComplexType:
    class Meta:
        name = "testComplexType"

    meta: List[MetaComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    product: List[ProductComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    expected_result: List[ExpectedResultComplexType] = field(
        default_factory=list,
        metadata={
            "name": "expectedResult",
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class TestResultComplexType:
    class Meta:
        name = "testResultComplexType"

    results: List[ResultsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )


@dataclass
class Testresult(TestResultComplexType):
    class Meta:
        name = "testresult"
        namespace = "http://momotor.org/1.0"


@dataclass
class TestsComplexType:
    class Meta:
        name = "testsComplexType"

    expected_result: List[ExpectedResultComplexType] = field(
        default_factory=list,
        metadata={
            "name": "expectedResult",
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    expect: List[ExpectComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    files: List[FilesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    properties: List[PropertiesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    test: List[TestComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )


@dataclass
class RecipeComplexType:
    class Meta:
        name = "recipeComplexType"

    meta: List[MetaComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    options: List[OptionsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    checklets: List[CheckletsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    files: List[FilesComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    steps: List[StepsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    tests: List[TestsComplexType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://momotor.org/1.0",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class Recipe(RecipeComplexType):
    class Meta:
        name = "recipe"
        namespace = "http://momotor.org/1.0"
