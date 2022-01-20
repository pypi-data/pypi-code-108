from Configurables import DaVinci, GaudiSequencer

from helpers import tuple_maker
from Bs2JpsiPhi import tuple_seq

seq = tuple_maker.tuple_sequence()
seq.Members += [tuple_seq]