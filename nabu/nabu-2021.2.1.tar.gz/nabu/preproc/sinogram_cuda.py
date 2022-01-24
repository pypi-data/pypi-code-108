from ..reconstruction.sinogram_cuda import *
from ..utils import deprecation_warning

deprecation_warning(
    "nabu.preproc.sinogram_cuda was moved to nabu.reconstruction.sinogram_cuda.",
    func_name="preproc_sinogram"
)