# -*- coding: utf-8 -*-
# @Author: Antoine Tavant
# @Date:   2022-01-21 13:21:38
# @Last Modified by:   Antoine Tavant
# @Last Modified time: 2022-01-25 09:33:24
import h5py


def descend_obj(obj,sep='\t'):
    """
    Iterate through groups in a HDF5 file and prints the groups and datasets names and datasets attributes
    """

    if type(obj) in [h5py._hl.group.Group, h5py._hl.files.File]:

        #print(obj.keys())
        for key in obj.keys():
            print(sep, '-', key, ':', obj[key])
            descend_obj(obj[key], sep=sep+'\t')

    elif type(obj)==h5py._hl.dataset.Dataset:
        keylist = ["unit", "time reference"]
        obj.attrs.keys()
        for key in keylist:
            try:
                print(sep+'\t', '-', key, ':', obj.attrs[key].decode(encoding="latin-1") )
            except KeyError:
                pass
            except UnicodeDecodeError:
                print(sep+'\t', '-', key, ':', obj.attrs[key] )



def h5dump(path,group='/'):
    """
    print HDF5 file metadata

    group: you can give a specific group, defaults to the root group
    """
    with h5py.File(path,'r') as f:

        descend_obj(f[group])
