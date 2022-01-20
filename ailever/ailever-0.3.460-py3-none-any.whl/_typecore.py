from ._version_info import version
import sys, os, re, pickle
import numpy as np
import pandas as pd
import torch
version = version

def BaseTypeCaster(obj=None, outtype='array'):
    assert outtype in ['BTC', 'list', 'dict', 'array', 'series', 'tensor', 'frame'], "outtype must be in 'BTC', 'list', 'dict', 'series', 'array', 'tensor', 'frame'"

    if obj is None:
        obj = _TypeCoreLoad(module_path=['ailever'], DS='AIL_DS_Base.pkl')
        return obj

    try:
        Dataset = _TypeCore()
        if isinstance(obj, (list,)):
            Dataset.list = obj
            Dataset.array = np.array(obj)
            Dataset.tensor = torch.tensor(obj)
            Dataset.frame = pd.DataFrame(obj)
        elif isinstance(obj, (np.ndarray,)):
            obj = obj.squeeze()
            Dataset.list = obj.tolist()
            Dataset.array = obj
            Dataset.tensor = torch.from_numpy(obj)
            Dataset.frame = pd.DataFrame(obj)
        elif isinstance(obj, (torch.Tensor,)):
            obj = obj.squeeze()
            Dataset.list = obj.tolist()
            Dataset.array = obj.numpy()
            Dataset.tensor = obj
            Dataset.frame = pd.DataFrame(obj.numpy())
        elif isinstance(obj, (pd.core.series.Series,)):
            Dataset.list = obj.values.tolist()
            Dataset.array = obj.values
            Dataset.tensor = torch.from_numpy(obj.values)
            Dataset.frame = pd.DataFrame(obj)
        elif isinstance(obj, (pd.core.frame.DataFrame,)):
            Dataset.list = obj.values.tolist()
            Dataset.array = obj.values
            Dataset.tensor = torch.from_numpy(obj.values)
            Dataset.frame = obj
    except:
        raise DataTypeError('Dataset must be symmetric in type of list, numpy.ndarray, torch.Tensor, pandas.core.series.Series, pandas.core.frame.DataFrame .')

    _TypeCoreSave(Dataset, module_path=['ailever'], DS='AIL_DS_Base.pkl')
    obj = _TypeCoreLoad(module_path=['ailever'], DS='AIL_DS_Base.pkl')

    if outtype == 'BTC':
        return obj
    else:
        obj = getattr(obj, outtype)
        return obj


class _TypeCore:
    def __init__(self):
        self.__list = None
        self.__dict = None
        self.__array = None
        self.__tensor = None
        self.__series = None
        self.__frame = None
        self.__etc = None

    @property
    def list(self):
        assert isinstance(self.__list, (list,)), 'list is not yet defined.'
        return self.__list
    
    @list.setter
    def list(self, data):
        assert isinstance(data, (list,)), 'Input data must has list-type.'
        self.__list = data

    @property
    def dict(self):
        assert isinstance(self.__dict, (dict,)), 'dict is not yet defined.'
        return self.__dict
    
    @dict.setter
    def dict(self, data):
        assert isinstance(data, (dict,)), 'Input data must has dict-type.'
        self.__dict = data

    @property
    def array(self):
        assert isinstance(self.__array, (np.ndarray,)), 'array is not yet defined.'
        return self.__array

    @array.setter
    def array(self, data):
        assert isinstance(data, (np.ndarray,)), 'Input data must has numpy.ndarray-type.'
        self.__array = data

    @property
    def tensor(self):
        assert isinstance(self.__tensor, (torch.Tensor,)), 'tensor is not yet defined.'
        return self.__tensor

    @tensor.setter
    def tensor(self, data):
        assert isinstance(data, (torch.Tensor,)), 'Input data must has torch.Tensor-type.'
        self.__tensor = data

    @property
    def series(self):
        assert isinstance(self.__series, (pd.core.series.Series,)), 'series is not yet defined.'
        return self.__series

    @series.setter
    def series(self, data):
        assert isinstance(data, (pd.core.series.Series,)), 'Input data must has pandas.core.series.Series-type.'
        self.__series = data

    @property
    def frame(self):
        assert isinstance(self.__frame, (pd.core.frame.DataFrame,)), 'frame is not yet defined.'
        return self.__frame

    @frame.setter
    def frame(self, data):
        assert isinstance(data, (pd.core.frame.DataFrame,)), 'Input data must has pandas.core.frame.DataFrame-type.'
        self.__frame = data

    @property
    def etc(self):
        return self.__etc

    @frame.setter
    def etc(self, data):
        self.__etc = data



def _TypeCoreLoad(module_path:list=['ailever'], DS='AIL_DS_Base.pkl')->'TypeCores':
    assert isinstance(module_path, (list,)), 'module_path argument must has list-type.'
    module_path = os.path.join(*module_path)

    pathcnt = 0
    for path in sys.path:
        if re.search('packages', os.path.basename(path)):
            # check path-right 
            if 'ailever' in os.listdir(path):
                for folder in os.listdir(path):
                    if re.search('ailever', folder):
                        if len(folder) > 7:
                            # ailever version
                            if folder[8:11] == version:
                                # check path-left 
                                for sep_path in path.split(os.path.sep):
                                    if re.search('PYTHON', sep_path.upper()):
                                        if len(sep_path) > 6:
                                            internal_py_version = list(sys.version.split()[0].replace('.',''))
                                            external_py_version = list(sep_path[6:].replace('.',''))
                                            split = min(len(internal_py_version),len(external_py_version))
                                            ipv = internal_py_version[:split]
                                            epv = external_py_version[:split]
                                            # python version
                                            if ipv == epv:
                                                pathcnt += 1
                                                if pathcnt > 1 : raise PathError('Check your python path.')
                                                _path = os.path.join(path, module_path, DS)
                                                with open(_path, 'rb') as f:
                                                    obj = pickle.load(f)
                                                assert isinstance(obj, (_TypeCore,)), 'obj argument must has _TypeCore-type.'
                                                return obj


def _TypeCoreSave(obj:_TypeCore, module_path:list=['ailever'], DS='AIL_DS_Base.pkl')->'TypeCores':
    assert isinstance(module_path, (list,)), 'module_path argument must have list-type.'
    assert isinstance(obj, (_TypeCore,)), 'obj argument must have _TypeCore-type.'
    module_path = os.path.join(*module_path)

    pathcnt = 0
    for path in sys.path:
        if re.search('packages', os.path.basename(path)):
            # check path-right 
            if 'ailever' in os.listdir(path):
                for folder in os.listdir(path):
                    if re.search('ailever', folder):
                        if len(folder) > 7:
                            # ailever version
                            if folder[8:11] == version:
                                # check path-left 
                                for sep_path in path.split(os.path.sep):
                                    if re.search('PYTHON', sep_path.upper()):
                                        if len(sep_path) > 6:
                                            internal_py_version = list(sys.version.split()[0].replace('.',''))
                                            external_py_version = list(sep_path[6:].replace('.',''))
                                            split = min(len(internal_py_version),len(external_py_version))
                                            ipv = internal_py_version[:split]
                                            epv = external_py_version[:split]
                                            # python version
                                            if ipv == epv:
                                                pathcnt += 1
                                                if pathcnt > 1 : raise PathError('Check your python path.')
                                                _path = os.path.join(path, module_path, DS)
                                                with open(_path, 'wb') as f:
                                                    pickle.dump(obj, f)


class DataTypeError(Exception) : pass
class PathError(Exception) : pass

