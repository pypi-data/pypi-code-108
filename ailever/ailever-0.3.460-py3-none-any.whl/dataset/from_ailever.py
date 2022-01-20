from .uci_machine_learning_repository import UCI_MLR
from .from_statsmodels import Statsmodels_API
from .from_sklearn import Sklearn_API

import pandas as pd


def Ailever_API(meta_info=True, table:str=None, download=False):
    if table is None:
        meta_table = pd.DataFrame(
                columns=['TABLE', 'DESCRIPTION'], 
                data=[['district0001', 'korea administrative district'], 
                    ])
        return meta_table
    else:
        table = pd.read_csv('https://raw.githubusercontent.com/ailever/dataset/main/{table.upper()}.csv', index_col=0)
        return table
    

class Integrated_Loader(Sklearn_API, Statsmodels_API):
    def __init__(self):
        pass
