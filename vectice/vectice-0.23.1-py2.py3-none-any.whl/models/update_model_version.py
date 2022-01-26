from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional, Union, List, Tuple

from .attachments import Attachments
from .with_properties import WithProperties


@dataclass
class UpdateModelVersion(WithProperties):
    algorithmName: Optional[str] = None
    description: Optional[str] = None
    data_properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None
    """"""

    def as_dict(self):
        return asdict(self)

    @staticmethod
    def create_attachments(attachments: Optional[List[str]]):
        if attachments is not None and len(attachments) >= 1:
            return Attachments("modelversion").with_attachments(attachments)
        return None

    def _create_with_property(self, data_properties: Tuple[str, str]):
        key, value = data_properties
        return self.with_property(key, value)

    def _create_with_properties(self, data_properties: List[Tuple[str, str]]):
        return self.with_properties(properties=data_properties)

    def add_properties(
        self, data_properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None
    ) -> UpdateModelVersion:
        if data_properties and isinstance(data_properties, list):
            self._create_with_properties(data_properties=data_properties)
        elif data_properties and isinstance(data_properties, tuple):
            self._create_with_property(data_properties=data_properties)
        return self
