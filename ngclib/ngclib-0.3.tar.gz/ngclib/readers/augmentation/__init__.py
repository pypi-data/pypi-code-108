from typing import Callable

from .ngc_augmentation import NGCAugmentation, GeneralPrototype, NodeSpecificPrototype
from .random_zoom import RandomZoom

def get_augmentation(name: str, **kwargs) -> Callable:
    if name == "random_zoom":
        return RandomZoom(**kwargs)

    assert False, f"Unknown augmentation: '{name}'"
