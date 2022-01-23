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
from omfit_classes.namelist import fortran_environment, sparray

__all__ = ['OMFITnamelist', 'OMFITfortranNamelist', 'fortran_environment', 'sparray']


class OMFITnamelist(namelist.NamelistFile, OMFITascii):
    r"""
    OMFIT class used to interface with FORTRAN namelist files
    """
    __doc__ += '\n'.join(namelist.NamelistFile.__doc__.strip().split('\n')[1:])

    def __init__(self, filename, **kw):
        kw.setdefault('collect_arrays', True)
        # convert int/float to 0 or 0.0 to allow correct save of OMFITproperties
        if isinstance(kw['collect_arrays'], dict):
            for item in kw['collect_arrays']:
                if (
                    isinstance(kw['collect_arrays'][item], dict)
                    and 'dtype' in kw['collect_arrays'][item]
                    and callable(kw['collect_arrays'][item]['dtype'])
                ):
                    kw['collect_arrays'][item]['dtype'] = kw['collect_arrays'][item]['dtype'](0.0)
        # we can delete 'collect_arrays' if True, because this is the default for the namelist.NamelistFile class
        if kw['collect_arrays'] is True:
            del kw['collect_arrays']

        # write `input_string` or `fromString` to file
        fromString = kw.pop('fromString', kw.pop('input_string', None))

        # place (1) in front of arrays/lists 1 element long so that they can be reloaded as such
        explicit_arrays = kw.pop('explicit_arrays', 1)

        OMFITascii.__init__(self, filename, fromString=fromString, **kw)
        namelist.NamelistFile.__init__(self, self.filename, explicit_arrays=explicit_arrays, **kw)

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """
        return namelist.NamelistFile.load(self)

    @property
    def equals(self):
        return self._equals

    @equals.setter
    def equals(self, value):
        # force namelist parse if the namelist output format has changed from the default
        list(self.keys())
        self._equals = value

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """
        return namelist.NamelistFile.save(self)


class OMFITfortranNamelist(OMFITnamelist):
    r"""
    OMFIT class used to interface with FORTRAN namelist files with arrays indexed according to FORTRAN indexing convention
    """
    __doc__ += '\n'.join(OMFITnamelist.__doc__.strip().split('\n')[1:])

    def __init__(self, *args, **kw):
        kw['index_offset'] = True
        OMFITnamelist.__init__(self, *args, **kw)


############################################
if '__main__' == __name__:
    test_classes_main_header()

    foo = OMFITnamelist(os.path.dirname(__file__) + '/../../samples/k139817.00109')
    foo.load()
    print(foo)
