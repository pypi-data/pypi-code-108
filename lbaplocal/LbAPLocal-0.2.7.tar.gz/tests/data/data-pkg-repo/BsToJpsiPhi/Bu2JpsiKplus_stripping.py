import os
import sys
sys.path.append(os.path.join(os.environ['ANALYSIS_PRODUCTIONS_BASE'], 'BsToJpsiPhi'))

from Configurables import DaVinci

from helpers.stripping import stripping

stripping_line = 'BetaSBu2JpsiKDetachedLine'
data_type = DaVinci().DataType

seq = stripping(data_type, stripping_line)
DaVinci().UserAlgorithms = [seq]
