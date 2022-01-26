from typing import Callable, Dict, List, Optional, Union

from pyarrow import Schema  # type: ignore
from pydantic import BaseModel

from tktl.core.t import EndpointKinds


class EndpointInfoSchema(BaseModel):
    name: str
    kind: EndpointKinds
    has_rest_sample_data: bool = False
    has_arrow_sample_data: bool = False
    profiling_supported: bool = False
    profiling_columns: Optional[List[str]] = []
    explain_input_names: Optional[List[str]] = []
    explain_input_example: Optional[List[Dict]] = []
    input_names: List[str] = []
    output_names: Union[str, List[str]] = []


class EndpointDefinition(BaseModel):
    name: str
    kind: str
    func: Callable
    input_schema: Optional[Union[Schema, bool]]
    output_schema: Optional[Union[Schema, bool]]
    has_sample_data: bool

    class Config:
        arbitrary_types_allowed = True
