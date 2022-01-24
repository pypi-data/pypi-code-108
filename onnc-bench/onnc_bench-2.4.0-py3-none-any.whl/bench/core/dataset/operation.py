from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict
import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dataset import Dataset



class DatasetOperation(ABC):
    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def append(self, obj, label=None):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def insert(self, index, obj):
        pass

    @abstractmethod
    def __getitem__(self, index: int):
        pass


class ONNCDatasetOperation(DatasetOperation):

    def load(self) -> None:
        pass

    def append_dir(self, path: Path, label_map: Dict = {},
                   suffix=['.jpg', '.jpeg', '.png', 'bmp']) -> None:
        for f in os.listdir(path):
            _f = path / Path(f)
            if _f.suffix.lower() in suffix:
                obj = _f.absolute()
                label = label_map[f] if f in label_map else None
                self.append(obj, label=label)

    def append(self, obj, label=None):
        self.dataset.src.append(obj)
        if label:
            self.dataset.y_label[str(len(self))] = label

    def remove(self, obj):
        pos = self.dataset.src.index(obj)
        self.dataset.src.remove(obj)
        del self.y_label[str(pos)]

    def insert(self, index, obj, label=None):
        self.dataset.src.insert(index, obj)
        self.dataset.y_label[id(obj)] = label

    def __getitem__(self, index: int):
        return self.dataset.src[index]

    def __len__(self):
        return len(self.dataset.src)

    def __iter__(self):
        return iter(self.dataset.src)


class ONNCImageDatasetOperation(ONNCDatasetOperation):
    def load(self):

        try:
            from PIL import Image
        except ImportError:
            print("Package Pillow/PIL is not found\nPlease install it using `pip install Pillow`")
        import numpy as np

        data = []
        for f in self.dataset.src:  # list of path
            image = Image.open(str(f))
            data.append(np.asarray(image))
        self.dataset.src = data
