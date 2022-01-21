from .dfFilter import  DfFilter
from .paramHandler import ParamHandler
from .dfStitcher import  DfStitcher

try:
    from . import dash_core_components as dcc
except:
    import dash_core_components as dcc


all = {DfFilter, ParamHandler, DfStitcher}