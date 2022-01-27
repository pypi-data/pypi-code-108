from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Callable, Any, Union, Dict, List, Iterator

from catalyst.core import Callback
from torch.optim import Optimizer
from torch.utils.data import DataLoader


@dataclass
class TrainingArguments(Mapping):
    num_epochs: int
    criterion: Optional[Callable] = None
    model: Optional[Callable] = None
    optimizer: Optional[Optimizer] = None
    scheduler: Optional[Any] = None
    logdir: Optional[Union[str, Path]] = None
    loaders: Optional[Dict[str, DataLoader]] = None
    callbacks: Optional[Union[List[Callback], Dict[str, Callback]]] = None
    fp16: Union[Dict, bool] = None
    catalyst_args: Dict = field(default_factory=lambda: {})
    train_transforms: Callable = None
    val_transforms: Callable = None

    def __getitem__(self, k):
        if hasattr(self, k):
            return getattr(self, k)
        return self.catalyst_args[k]

    def __len__(self) -> int:
        return len(self.__dataclass_fields__) + len(self.catalyst_args)

    def __iter__(self) -> Iterator:
        res = {}
        for field_name in self.__dataclass_fields__:
            if field_name != 'catalyst_args':
                attr = getattr(self, field_name)
                if attr is not None:
                    res[field_name] = attr
        for key, value in self.catalyst_args.items():
            res[key] = value
        return iter(res)