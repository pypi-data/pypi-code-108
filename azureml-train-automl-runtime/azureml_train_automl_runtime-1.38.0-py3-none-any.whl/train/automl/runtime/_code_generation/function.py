# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Iterable, List, Optional, Union

from azureml.automl.core import _codegen_utilities
from azureml.automl.core._codegen_utilities import ImportInfoType


class Function:
    def __init__(self, function_name: str, *params: str):
        self.function_name = function_name
        self.param_list = params
        self.imports = []  # type: List[ImportInfoType]
        self.body = []  # type: List[str]

    def add_imports(self, *objs: Any) -> None:
        for obj in objs:
            self.imports.append(_codegen_utilities.get_import(obj))

    def add_import_tuples(self, objs: List[ImportInfoType]) -> None:
        self.imports.extend(objs)

    def __iadd__(self, other: Union[List[str], str]) -> "Function":
        if isinstance(other, str):
            self.body.append(other)
        elif isinstance(other, list):
            self.body.extend(other)
        else:
            raise ValueError(f"Cannot add type {other.__class__.__name__} to f{self.__class__.__name__}")
        return self

    def add_lines(self, *lines: str) -> None:
        self.body.extend(lines)

    def generate_code(self) -> List[str]:
        output = [f"def {self.function_name}({', '.join(self.param_list)}):"]
        output.extend(_codegen_utilities.generate_import_statements(self.imports))
        output.append("")
        output.extend(self.body)
        return _codegen_utilities.indent_function_lines(output)
