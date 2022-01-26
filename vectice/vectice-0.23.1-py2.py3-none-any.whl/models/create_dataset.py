from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional, List, Union, Tuple
from .with_properties import WithProperties
from .with_tags import WithTags


@dataclass
class CreateDataset(WithProperties, WithTags):
    name: Optional[str] = None
    connectionId: Optional[int] = None
    connectionName: Optional[str] = None
    notes: Optional[str] = None
    files: Optional[List[str]] = None
    folders: Optional[List[str]] = None
    data_properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None
    data_tags: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None

    def _create_with_property(self, data_properties: Tuple[str, str]):
        key, value = data_properties
        return self.with_property(key, value)

    def _create_with_properties(self, data_properties: List[Tuple[str, str]]):
        return self.with_properties(properties=data_properties)

    def add_properties(
        self, data_properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None
    ) -> CreateDataset:
        if data_properties and isinstance(data_properties, list):
            self._create_with_properties(data_properties=data_properties)
        elif data_properties and isinstance(data_properties, tuple):
            self._create_with_property(data_properties=data_properties)
        return self

    def _create_with_tag(self, data_tags: Tuple[str, str]):
        key, value = data_tags
        return self.with_tag(key, value)

    def _create_with_tags(self, data_tags: List[Tuple[str, str]]):
        return self.with_tags(tags=data_tags)

    def add_tags(self, data_tags: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None) -> CreateDataset:
        if data_tags and isinstance(data_tags, list):
            self._create_with_tags(data_tags=data_tags)
        elif data_tags and isinstance(data_tags, tuple):
            self._create_with_tag(data_tags=data_tags)
        return self

    def as_dict(self):
        dataset = asdict(self)
        dataset_clean = dataset.copy()
        for key, value in dataset.items():
            if value is None:
                del dataset_clean[key]
            if key == "notes" and value is not None:
                dataset_clean["description"] = dataset_clean.pop("notes")
        return dataset_clean
