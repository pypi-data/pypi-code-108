# COMPAT.
from ..utils import deprecated_class
from ..reconstruction.rings_cuda import CudaMunchDeringer as CudaMunchDeringer_

CudaMunchDeringer = deprecated_class(
    "preproc.rings was moved to reconstruction.rings",
    do_print=True
)(CudaMunchDeringer_)
