import os

from Configurables import (
    DaVinci,
    MCDecayTreeTuple,
)


from DecayTreeTuple.Configuration import *

from cbtesting.helpers import decay_descriptors 

def mc_tuple_maker():
    """Return a sequence for producing ntuples.

    Assumes the decay structure is like:

        Beauty -> (J/Psi -> l- l+) (Lambda0 -> p pi-)
    """

    sample_decay   = DaVinci().TupleFile # FOR EXAMPLE Bd2KsJpsee

    # FOR LOADING DECAY DESCRIPTORS, SETTING BRANCHES, ETC.
    decay_desc_full           = decay_descriptors.dict_mc[sample_decay]
    tuple_branches, part_list = decay_descriptors.tuple_branches(decay_desc_full)
    print ('Decay desc',decay_desc_full)   
    print ('branches',tuple_branches)

    decay_desc_noV0dec         = decay_descriptors.dict_mc_noV0dec[sample_decay]
    tuple_branches_noV0dec, part_list = decay_descriptors.tuple_branches(decay_desc_noV0dec)
    print ('Decay desc',decay_desc_noV0dec) 
    print ('branches',tuple_branches_noV0dec)
  

    tool_list = [
        'MCTupleToolKinematic',
        'MCTupleToolHierarchy',
        'MCTupleToolPID',
        'MCTupleToolReconstructed'
    ]

    mctree = MCDecayTreeTuple('MCTuple')
    for tool in tool_list:  mctree.ToolList += [tool]
    
    mctree.Decay    = decay_desc_full
    mctree.Branches = tuple_branches
    DaVinci().UserAlgorithms += [mctree]

    if 'L0' in tuple_branches or 'K0' in tuple_branches:
        mctree_noV0dec = mctree.clone("MCTuple_NoV0Dec")
        mctree_noV0dec.Decay    = decay_desc_noV0dec
        mctree_noV0dec.Branches = tuple_branches_noV0dec
        DaVinci().UserAlgorithms += [mctree_noV0dec]

    return True

mc_tuple_maker()
