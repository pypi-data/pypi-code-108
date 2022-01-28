import sys
import importlib

__all__ = ['QT_LIB']
DChan = None

qts = ['PyQt5', 'PyQt4']
QT_LIB = None
cda = None

for lib in qts:
    if lib in sys.modules:
        QT_LIB = lib
        break
if QT_LIB is None:
    for lib in qts:
        try:
            importlib.import_module(lib)
            QT_LIB = lib
            break
        except ImportError:
            pass
if QT_LIB is None:
    ImportError("PyQt not found. it's required for qcda")

if QT_LIB == 'PyQt5':
    import pycx4.q5cda
    __all__ += pycx4.q5cda.__all__
    # get q5cda to qcda namespace
    from pycx4.q5cda import *
elif QT_LIB == 'PyQt4':
    import pycx4.q4cda
    __all__ += pycx4.q4cda.__all__
    # get q5cda to qcda namespace
    from pycx4.q4cda import *
else:
    ImportError("something wrong")

