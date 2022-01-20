import os
import sys

WORKING_DIR = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(WORKING_DIR)

from superannotate_schemas.validators import AnnotationValidators


__version__ = '1.0.35'

__all__ = [
    "__version__",
    "AnnotationValidators"
]

