from .._typecore import _TypeCore, _TypeCoreLoad, _TypeCoreSave, BaseTypeCaster
import numpy as np
import pandas as pd
import torch

def LanguageTypeCaster(obj, outtype='array'):
    obj = BaseTypeCaster(obj, outtype='BTC')

    obj.list = [1,2,3]
    obj.array = np.array([1,2,3])
    obj.tensor = torch.tensor([1,2,3])
    obj.frame = pd.DataFrame([1,2,3])
    _TypeCoreSave(obj, module_path=['ailever', 'language'], DS='AIL_DS_Language.pkl')
    obj = _TypeCoreLoad(module_path=['ailever', 'language'], DS='AIL_DS_Language.pkl')
    return obj
