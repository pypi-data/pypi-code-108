from dataclasses import dataclass

import numpy as np
from bunch import Bunch


@dataclass
class StyleProduct:
    styling_hash: str
    styling_config: Bunch
    synthesized_image: np.ndarray
