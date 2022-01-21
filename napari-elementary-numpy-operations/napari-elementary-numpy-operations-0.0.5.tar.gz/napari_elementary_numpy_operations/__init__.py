from .napari_numpy import napari_experimental_provide_dock_widget


try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


def get_module_version():
    return __version__


