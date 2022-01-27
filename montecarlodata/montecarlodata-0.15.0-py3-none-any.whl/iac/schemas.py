import json
from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import LetterCase
from dataclasses_json import dataclass_json
from marshmallow import fields

from montecarlodata.iac.utils import field_spec
from montecarlodata.settings import DEFAULT_MONTECARLO_MONITOR_CONFIG_VERSION, DEFAULT_INCLUDE_PATTERNS, DEFAULT_EXCLUDE_PATTERNS


@dataclass_json
@dataclass
class ProjectConfig:
    version: Optional[int] = field_spec(fields.Int(required=False), default_factory=lambda: DEFAULT_MONTECARLO_MONITOR_CONFIG_VERSION)
    default_resource: Optional[str] = field_spec(fields.Str(required=False))
    include_file_patterns: Optional[List[str]] = field_spec(
        fields.List(fields.Str(required=True)),
        default_factory=lambda: DEFAULT_INCLUDE_PATTERNS)
    exclude_file_patterns: Optional[List[str]] = field_spec(
        fields.List(fields.Str(required=True)),
        default_factory=list)

    def __post_init__(self):
        self.exclude_file_patterns = list(set(self.exclude_file_patterns + DEFAULT_EXCLUDE_PATTERNS))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ResourceModification:
    type: str
    description: str
    resource_as_json: str

    def __post_init__(self):
        self.resource = json.loads(self.resource_as_json)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfigTemplateUpdateResponse:
    resource_modifications: List[ResourceModification]
    errors_as_json: Optional[str] = None
    changes_applied: bool = False

    def __post_init__(self):
        self.errors = json.loads(self.errors_as_json)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfigTemplateDeleteResponse:
    num_deleted: int
    changes_applied: bool = False