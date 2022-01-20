from .._typecore import _TypeCore, _TypeCoreLoad, _TypeCoreSave, BaseTypeCaster
import numpy as np
import pandas as pd
import torch

def MachineTypeCaster(obj, outtype='array'):
    obj = BaseTypeCaster(obj, outtype='BTC')

    obj.list = [1,2,3]
    obj.array = np.array([1,2,3])
    obj.tensor = torch.tensor([1,2,3])
    obj.frame = pd.DataFrame([1,2,3])
    _TypeCoreSave(obj, module_path=['ailever', 'machine'], DS='AIL_DS_Machine.pkl')
    obj = _TypeCoreLoad(module_path=['ailever', 'machine'], DS='AIL_DS_Machine.pkl')
    return obj
