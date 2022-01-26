# import Qt before pyqtgraph, so version gets set correctly
import qtpy
import pyqtgraph as pg


try:
    from .__version__ import version as __version__
except ModuleNotFoundError:
    try:
        import setuptools_scm
        __version__ = setuptools_scm.get_version(fallback_version='?.?.?')
    # FIXME: fallback_version is not available in the buster version
    # (3.2.0-1)
    except TypeError:
        __version__ = setuptools_scm.get_version()
    except LookupError:
        __version__ = '?.?.?'
