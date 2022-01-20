"""Set up the main and tuple sequences.

The MainSeq sequence is set as the sole member of DaVinci().UserAlgorithms.
It contains:

1. CheckPV algorithm.
2. TrackSmearState algorithm if MC, else TrackScaleState.
3. Tuple sequence, as returned by helpers.tuple_maker.tuple_sequence.

Ntuple algorithms should be added to the TupleSeq sequence, which runs in
non-lazy OR mode.

The DaVinci().Simulation property must be set before this options file is run.
"""
import os
import sys
sys.path.append(os.path.join(os.environ['ANALYSIS_PRODUCTIONS_BASE'], 'BsToJpsiPhi'))

from Configurables import (
    CheckPV,
    DaVinci,
    GaudiSequencer,
    TrackScaleState,
    TrackSmearState
)

from helpers import tuple_maker

if DaVinci().Simulation:
    track_alg = TrackSmearState('TrackSmearState')
else:
    track_alg = TrackScaleState('TrackScaleState')

main_seq = GaudiSequencer('MainSeq')
main_seq.Members = [
    CheckPV(),
    track_alg,
    tuple_maker.tuple_sequence()
]

DaVinci().UserAlgorithms = [main_seq]
