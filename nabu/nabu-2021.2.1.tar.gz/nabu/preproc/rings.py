# COMPAT.
from ..utils import deprecated_class
from ..reconstruction.rings import MunchDeringer as MunchDeringer_, munchetal_filter as munchetal_filter_

MunchDeringer = deprecated_class(
    "preproc.rings was moved to reconstruction.rings",
    do_print=True
)(MunchDeringer_)
munchetal_filter = deprecated_class(
    "preproc.rings was moved to reconstruction.rings",
    do_print=True
)(munchetal_filter_)
