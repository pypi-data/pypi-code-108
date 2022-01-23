import os as _os
import sys

# This is a junction point in the OMFIT import system
#
# if `omfit_classes.startup_framework` is found in the sys.modules, it means that the whole framework was started
# else it means that only the classes modules have been imported in a Python session.
# The difference between startup_framework and startup_classes is that the former runs utils_base and externalImports,
# which notably imports matplotlib, tk and pylab. The startup_classes script instead only imports utils_base.

OMFITsrc = _os.path.abspath(_os.path.dirname(_os.path.dirname(__file__)))
_path = _os.path.abspath(OMFITsrc)
if _path not in sys.path:
    sys.path.insert(0, _path)

if 'omfit_classes.startup_framework' in sys.modules:
    # FRAMEWORK
    sys.modules['omfit_classes.startup_choice'] = sys.modules['omfit_classes.startup_framework']
else:
    # CLASSES
    _path = _os.path.abspath(OMFITsrc + _os.sep + 'omfit_classes')
    if _path not in sys.path:
        sys.path.insert(0, _path)
    from startup_classes import *
