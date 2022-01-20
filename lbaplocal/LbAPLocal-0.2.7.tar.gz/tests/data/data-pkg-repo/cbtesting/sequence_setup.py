"""Set up the main and tuple sequences.

The MainSeq sequence is set as the sole member of DaVinci().UserAlgorithms.
Ntuple algorithms should be added to the TupleSeq sequence, which runs in
non-lazy OR mode.

The DaVinci().Simulation property must be set before this options file is run.
"""
from Configurables import (
    DaVinci,
    GaudiSequencer,
)

from cbtesting.helpers import tuple_maker

main_seq = GaudiSequencer('MainSeq')
main_seq.Members = [
    tuple_maker.tuple_sequence(),
]

DaVinci().UserAlgorithms = [main_seq]

# ONLY CONFIG NEEDED
tuple_names = [
     'Lb2JpsiL_eeTuple',
     'Lb2JpsiL_mmTuple',
     'Lb2LemuTuple',
     'Lb2Lee_SSTuple',
     'Lb2Lmm_SSTuple',
     'Lb2Lemu_SSTuple',
     'Bu2JpsiK_eeTuple',
     'Bu2JpsiK_mmTuple',
     'Bd2JpsiKs_eeTuple',
     'Bd2JpsiKs_mmTuple',
    ]

for tuple_name in tuple_names:
    use_upstream_electrons = False
    if 'ee' in tuple_name and not 'SS' in tuple_name: 
        use_upstream_electrons = True
    tuple_maker.tuple_maker( tuple_name, upstream_electrons=use_upstream_electrons) 



