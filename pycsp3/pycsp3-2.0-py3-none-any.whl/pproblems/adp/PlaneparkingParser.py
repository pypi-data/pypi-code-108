from pandas import *
from pycsp3.problems.data.parsing import *


def createObject(name, file):
    xls = ExcelFile(file)
    df = xls.parse(xls.sheet_names[0])
    data[name] = dict()
    for key, value in df.to_dict().items():
        data[name][key] = list(value.values())

prefix = "pproblems/adp/excel_data/"


createObject('capacites', prefix +'capacites.xlsx')
createObject('ombrages', prefix + 'ombrages.xlsx')
createObject('ordonnancement', prefix + 'ordonnancement.xlsx')
createObject('parkings', prefix + 'parkings.xlsx')
createObject('reductions', prefix + 'reductions.xlsx')
createObject('strategies', prefix + 'strategies_matrice.xlsx')
createObject('ordonnancement', prefix + 'ordonnancement.xlsx')
createObject('traitement', prefix + 'temps_traitement.xlsx')
createObject('vols', prefix + 'vols.xlsx')
createObject('volsStrategies', prefix + 'vols_strat.xlsx')


