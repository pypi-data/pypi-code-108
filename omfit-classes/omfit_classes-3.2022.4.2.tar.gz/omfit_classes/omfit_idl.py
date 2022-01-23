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

from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes import namelist

__all__ = ['OMFITidl']


class OMFITidl(namelist.NamelistFile, OMFITascii):
    r"""
    OMFIT class used to interface with IDL language files (with only declarations in it)

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        tmp = self.filename
        namelist.NamelistFile.__init__(self, None, idlInput=True, **kw)
        self.filename = tmp
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """
        return namelist.NamelistFile.load(self)

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """
        return namelist.NamelistFile.save(self)
