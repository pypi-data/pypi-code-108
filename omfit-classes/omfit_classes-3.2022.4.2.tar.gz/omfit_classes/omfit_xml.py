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

try:
    import xmltodict
except ImportError:
    xmltodict = None
import numpy as np

__all__ = ['OMFITxml']


def recursive_interpreter(me, interpret_method=ast.literal_eval):
    """
    Traverse dictionaries and list to convert strings to int/float when appropriate

    :param me: root of the dictionary to traverse

    :param interpret_method: method used for conversion (ast.literal_eval by default)

    :return: root of the dictionary
    """
    if isinstance(me, list):
        keys = range(len(me))
    elif isinstance(me, dict):
        keys = me.keys()

    for kid in keys:
        if me[kid] is None:
            continue
        elif isinstance(me[kid], (list, dict)):
            recursive_interpreter(me[kid], interpret_method=interpret_method)
        else:
            try:
                me[kid] = interpret_method(me[kid])
            except (ValueError, SyntaxError) as _excp:
                pass
            if isinstance(me[kid], str) and ' ' in me[kid]:
                try:
                    values = []
                    for item in re.split('[ |\t]+', me[kid].strip()):
                        values.extend(tolist(float(item)))
                    me[kid] = np.array(values)
                except ValueError:
                    pass

    return me


def recursive_encoder(me):
    """
    Traverse dictionaries and list to convert entries strings as appropriate

    :param me: root of the dictionary to traverse

    :return: root of the dictionary
    """
    if isinstance(me, list):
        keys = range(len(me))
    elif isinstance(me, dict):
        keys = me.keys()

    for kid in keys:
        if me[kid] is None:
            continue
        elif isinstance(me[kid], (list, dict)):
            recursive_encoder(me[kid])
        else:
            if isinstance(me[kid], np.ndarray):
                me[kid] = ' '.join([repr(x) for x in me[kid]])
            else:
                me[kid] = str(me[kid])
    return me


class OMFITxml(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with XML input files

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        self.clear()
        with open(self.filename, 'r') as f:
            self.update(xmltodict.parse(f.read()))
        recursive_interpreter(self)

    @dynaSave
    def save(self):
        tmp = copy.deepcopy(self)
        recursive_encoder(tmp)
        with open(self.filename, 'w') as f:
            f.write(xmltodict.unparse(tmp, pretty=True))


############################################
if '__main__' == __name__ and xmltodict is not None:
    test_classes_main_header()

    tmp = OMFITxml(OMFITsrc + '/../samples/chease_input_imas_std_pjphi.xml')
    tmp.load()
    tmp.save()
