from ._typecore import _TypeCore, _TypeCoreLoad, _TypeCoreSave, BaseTypeCaster
import numpy as np
import pandas as pd
import torch

def ForecastTypeCaster(obj=None, outtype='array'):
    assert outtype in ['FTC', 'BTC', 'list', 'dict', 'array', 'series', 'tensor', 'frame'], "outtype must be in 'BTC', 'list', 'dict', 'series', 'array', 'tensor', 'frame'"

    obj = BaseTypeCaster(obj, outtype='BTC')
    _TypeCoreSave(obj, module_path=['ailever', 'forecast'], DS='AIL_DS_Forecast.pkl')
    obj = _TypeCoreLoad(module_path=['ailever', 'forecast'], DS='AIL_DS_Forecast.pkl')

    if outtype == 'FTC':
        return obj
    else:
        obj = getattr(obj, outtype)
        return obj
