from ..reconstruction.sinogram import *
from ..utils import deprecation_warning

deprecation_warning(
    "nabu.preproc.sinogram was moved to nabu.reconstruction.sinogram.",
    func_name="preproc_sinogram"
)