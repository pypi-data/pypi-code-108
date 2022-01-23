try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

__all__ = ['OMFITerror', 'OMFITobjectError', 'OMFITexpressionError']


class OMFITerror(object):
    def __init__(self, error='Error', traceback=None):
        self.error = error
        self.traceback = traceback

    def __repr__(self):
        return self.error


class OMFITobjectError(OMFITerror, OMFITobject, SortedDict):
    """
    This class is a subclass of OMFITobject and is used in OMFIT
    when loading of an OMFITobject subclass object goes wrong
    during the loading of a project.

    Note that the orifinal file from which the loading failed is not lost
    but can be accessed from the .filename attribute of this object.
    """

    def __init__(self, filename, className=None, traceback=None, **kw):
        SortedDict.__init__(self)
        OMFITobject.__init__(self, filename, **kw)
        errorMessage = 'Error with OMFITobject ' + os.path.split(filename)[1]
        if className is not None:
            errorMessage += ' of class ' + className
        self.error = kw.pop('error', errorMessage)
        self.className = className
        self.traceback = traceback

    def __tree_repr__(self):
        return os.path.split(self.filename)[-1] + '  ' + self.error, []


class OMFITexpressionError(OMFITerror):
    def __init__(self, error='Expression Error', **kw):
        OMFITerror.__init__(self, error, **kw)
