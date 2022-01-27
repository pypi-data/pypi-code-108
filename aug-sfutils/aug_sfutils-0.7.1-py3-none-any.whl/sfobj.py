import numpy as np


class SFOBJ(np.ndarray):
    """
    Subclass of numpy.ndarray adding a few metadata,
    such as physical unit, description and relations
    """

    def __new__(cls, input_array, sfho=None):

        obj = np.asarray(input_array).view(cls)
        for attr, val in sfho.__dict__.items():
            obj.__dict__[attr] = val
        return obj

    def __array_finalize__(self, obj):

        if obj is None: return
        for attr in ('objnam', 'obj_type', 'object_type', 'level', 'status', 'errcode', 'rel', 'relations', 'address', 'length', 'descr', 'data_format', 'physunit', 'phys_unit', 'stat_ext', 'n_pre', 'n_steps', 'tbase_type'):
            self.__dict__[attr] = getattr(obj, attr, None)
