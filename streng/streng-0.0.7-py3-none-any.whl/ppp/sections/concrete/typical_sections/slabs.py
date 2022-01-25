from dataclasses import dataclass, field

@dataclass
class Slab:
    l_max: float
    l_min: float
    slab_type: str