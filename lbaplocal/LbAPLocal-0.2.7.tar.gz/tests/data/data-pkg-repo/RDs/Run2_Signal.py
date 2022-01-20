import os
import sys

if 'ANALYSIS_PRODUCTIONS_BASE' in os.environ:
    sys.path.append(os.path.join(os.environ['ANALYSIS_PRODUCTIONS_BASE'], 'RDs'))
else:
    sys.path.append(os.getcwd())

from Configurables import DaVinci
from helpers import signal_tuple_maker


# DaVinci().Simulation = True 
# DaVinci().InputType = 'DST'
# DaVinci().DataType = '2018'
# DaVinci().PrintFreq = 5000
# MagnetPolarity = 'MD'
# DaVinci().EvtMax = -1

# DaVinci().Lumi = not DaVinci().Simulation
# DaVinci().TupleFile = 'Bsntuple_MC.root'
# DaVinci().DDDBtag = "dddb-20170721-3"
# CondDB_tag  = "sim-20190430-vc"
# if MagnetPolarity == 'MU':
#     DaVinci().CondDBtag = CondDB_tag + "-mu100"
# elif MagnetPolarity == 'MD':
#     DaVinci().CondDBtag = CondDB_tag + "-md100"

signal_tuple_maker.addNtupleToDaVinci(DaVinci().Simulation, 'RXcHad.Strip', 'Bs2DsTauNuForB2XTauNuAllLines')
