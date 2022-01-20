import os

from Configurables import (
    BTaggingTool,
    DaVinci,
    GaudiSequencer,
    MCDecayTreeTuple,
    MCTupleToolP2VV
)

from FlavourTagging.Tunings import applyTuning as applyFTTuning
from PhysSelPython.Wrappers import (
    AutomaticData,
    FilterSelection,
    SelectionSequence,
    TupleSelection
)


L0_LINES = [
    'L0DiMuonDecision',
    'L0GlobalDecision',
    'L0MuonDecision'
]
HLT1_LINES = [
    'Hlt1DiMuonHighMassDecision',
    'Hlt1DiMuonLowMassDecision',
    'Hlt1DiMuonNoL0Decision',
    'Hlt1GlobalDecision',
    'Hlt1L0AnyDecision',
    'Hlt1SingleMuonHighPTDecision',
    'Hlt1TrackMVADecision',
    'Hlt1TrackMVALooseDecision',
    'Hlt1TrackMuonDecision',
    'Hlt1TrackMuonMVADecision',
    'Hlt1TwoTrackMVADecision',
    'Hlt1TwoTrackMVALooseDecision'
]
HLT2_LINES = [
    'Hlt2DiMuonDecision',
    'Hlt2DiMuonDetachedDecision',
    'Hlt2DiMuonDetachedHeavyDecision',
    'Hlt2DiMuonDetachedJPsiDecision',
    'Hlt2DiMuonDetachedPsi2SDecision',
    'Hlt2DiMuonJPsiDecision',
    'Hlt2SingleMuonDecision',
    'Hlt2SingleMuonHighPTDecision',
    'Hlt2SingleMuonLowPTDecision',
    'Hlt2SingleMuonRareDecision',
    'Hlt2SingleMuonVHighPTDecision',
    'Hlt2Topo2BodyDecision',
    'Hlt2Topo3BodyDecision',
    'Hlt2Topo4BodyDecision',
    'Hlt2TopoMu2BodyDecision',
    'Hlt2TopoMu3BodyDecision',
    'Hlt2TopoMu4BodyDecision',
    'Hlt2TopoMuMu2BodyDecision',
    'Hlt2TopoMuMu3BodyDecision',
    'Hlt2TopoMuMu4BodyDecision'
]
TRIGGER_LINES = L0_LINES + HLT1_LINES + HLT2_LINES


def tuple_maker(name, decay, branches, stripping_line, is_mc, input_type, refit_pvs=True):
    """Return a sequence for producing ntuples.

    Assumes the decay structure is like:

        Beauty -> (J/psi -> mu- mu+) X

    The `name` arg must start with Bu, Bd, or Bs. This is used to
    determine the head of the decay.
    """
    assert name.startswith(('Bu', 'Bd', 'Bs')), 'Unknown decay head in `name`'
    # Parse the name to get the decay head
    decay_head = {
        'Bu': 'B+',
        'Bd': 'B0',
        'Bs': 'B_s0'
    }[name[:2]]
    # Assume we're processing a P2VV decay for neutral B's, in which case we'll
    # add some extra tools later
    p2vv = decay_head in ['B0', 'B_s0']

    # TODO: consider moving this block out of this method
    is_mdst = input_type.upper() == 'MDST'
    # Don't get the tagging decision on MC microDSTs
    with_ft = not (is_mc and is_mdst)
    tes_root = ''
    if is_mc:
        tes_root = '/Event/AllStreams'
    else:
        if is_mdst:
            tes_root = '/Event/Leptonic'
        else:
            tes_root = '/Event/Dimuon'
    if is_mdst:
        DaVinci().RootInTES = tes_root
    location = 'Phys/{}/Particles'.format(stripping_line)
    if not is_mdst:
        location = os.path.join(tes_root, location)

    tuple_input = AutomaticData(location)
    # Require that there are valid PVs after refitting, as required by
    # TupleToolPropertime
    if refit_pvs:
        tuple_input = FilterSelection(
            'CheckRefittedPVs_{}'.format(name),
            [tuple_input],
            Code='BPVVALID()',
            ReFitPVs=True
        )

    tools = [
        'TupleToolANNPID',
        'TupleToolEventInfo',
        'TupleToolKinematic',
        'TupleToolL0Calo',
        'TupleToolL0Data',
        'TupleToolPid',
        'TupleToolPrimaries',
        'TupleToolPropertime',
        'TupleToolTISTOS'
    ]
    if is_mc:
        tools += [
            'TupleToolMCBackgroundInfo'
        ]

    tuple_selection = TupleSelection(
        '{}_Tuple'.format(name),
        [tuple_input],
        decay,
        ToolList=tools,
        ReFitPVs=refit_pvs
    )
    dtt = tuple_selection.algorithm()
    dtt.addBranches(branches)

    geom = dtt.addTupleTool('TupleToolGeometry')
    geom.RefitPVs = refit_pvs
    geom.Verbose = True

    reco_stats = dtt.addTupleTool('TupleToolRecoStats')
    reco_stats.Verbose = True

    track_inf = dtt.addTupleTool('TupleToolTrackInfo')
    track_inf.Verbose = True

    track_pos = dtt.addTupleTool('TupleToolTrackPosition')
    track_pos.Z = 7500.0

    trig_tool = dtt.addTupleTool('TupleToolTrigger')
    trig_tool.Verbose = True
    trig_tool.TriggerList = TRIGGER_LINES
    trig_tool.OutputLevel = 6

    b_tistos = dtt.B.addTupleTool('TupleToolTISTOS')
    b_tistos.Verbose = True
    b_tistos.TriggerList = TRIGGER_LINES

    jpsi_tistos = dtt.Jpsi.addTupleTool('TupleToolTISTOS')
    jpsi_tistos.Verbose = True
    jpsi_tistos.TriggerList = TRIGGER_LINES

    LoKi_B = dtt.B.addTupleTool('LoKi::Hybrid::TupleTool/LoKi_B')
    LoKi_B.Variables = {
        # TODO: do we really need this? I'm pretty sure this is just equivalent
        # to the B mass. Otherwise, will need to know the B decay products
        # 'JpsiPhiMass': 'WM(\'J/psi(1S)\',\'phi(1020)\')',
        'ETA': 'ETA',
        'DOCA': 'DOCA(1,2)',
        'Y': 'Y',
        'LV01': 'LV01',
        'LV02': 'LV02',
        'LOKI_FDCHI2': 'BPVVDCHI2',
        'LOKI_FDS': 'BPVDLS',
        'LOKI_DIRA': 'BPVDIRA',
        'LOKI_DTF_CTAU': 'DTF_CTAU(0, True)',
        'LOKI_DTF_CTAUS': 'DTF_CTAUSIGNIFICANCE(0, True)',
        'LOKI_DTF_CHI2NDOF': 'DTF_CHI2NDOF(True)',
        'LOKI_DTF_CTAUERR': 'DTF_CTAUERR(0, True)',
        'LOKI_MASS_JpsiConstr': 'DTF_FUN(M, True, \'J/psi(1S)\')',
        'LOKI_DTF_VCHI2NDOF': 'DTF_FUN(VFASPF(VCHI2/VDOF), True)'
    }

    LoKi_Jpsi = dtt.Jpsi.addTupleTool('LoKi::Hybrid::TupleTool/LoKi_Jpsi')
    LoKi_Jpsi.Variables = {
        'ETA': 'ETA',
        'Y': 'Y',
        'LV01': 'LV01',
        'LV02': 'LV02',
        'LOKI_FDCHI2': 'BPVVDCHI2',
        'LOKI_FDS': 'BPVDLS',
        'LOKI_DIRA': 'BPVDIRA'
    }

    LoKi_muonp = dtt.muplus.addTupleTool('LoKi::Hybrid::TupleTool/LoKi_muonp')
    LoKi_muonm = dtt.muminus.addTupleTool('LoKi::Hybrid::TupleTool/LoKi_muonm')
    LoKi_muonp.Variables = LoKi_muonm.Variables = {
        'LOKI_ETA': 'ETA',
        'LOKI_Y': 'Y'
    }

    # refit with constraints
    fitter_params = [
        ('ConstJpsi', True, ['J/psi(1S)']),
        ('ConstJpsiNoPV', False, ['J/psi(1S)']),
        ('ConstBJpsi', True, [decay_head, 'J/psi(1S)']),
        ('ConstOnlyPV', True, [])
    ]
    # Only the Bd2JpsiKstar tuple has this fitter configuration
    if decay_head == 'B0':
        fitter_params += [
            ('ConstBJpsiNoPV', False, [decay_head, 'J/psi(1S)'])
        ]
    for fitter_name, constrain_to_pv, daughter_constraints in fitter_params:
        fitter = dtt.B.addTupleTool('TupleToolDecayTreeFitter/{}'.format(fitter_name))
        fitter.Verbose = True
        fitter.UpdateDaughters = True
        fitter.constrainToOriginVertex = constrain_to_pv
        fitter.daughtersToConstrain = daughter_constraints

    if with_ft:
        btag = dtt.addTupleTool('TupleToolTagging')
        # Take the tagging decision from microDSTs, otherwise recompute it
        if is_mdst:
            btag.UseFTfromDST = True
        else:
            btag.Verbose = True
            btag.AddMVAFeatureInfo = True

            btagtool = btag.addTool(BTaggingTool, name='MyBTaggingTool_{}'.format(name))

            applyFTTuning(btagtool, tuning_version='Summer2017Optimisation_v4_Run2')
            btag.TaggingToolName = btagtool.getFullName()

    LoKi_EvtTuple = dtt.addTupleTool('LoKi::Hybrid::EvtTupleTool/LoKi_EvtTuple')
    LoKi_EvtTuple.VOID_Variables = {
        'LoKi_nPVs': "CONTAINS('Rec/Vertex/Primary')",
        'LoKi_nSpdMult': "CONTAINS('Raw/Spd/Digits')",
        'LoKi_nVeloClusters': "CONTAINS('Raw/Velo/Clusters')",
        'LoKi_nVeloLiteClusters': "CONTAINS('Raw/Velo/LiteClusters')",
        'LoKi_nITClusters': "CONTAINS('Raw/IT/Clusters')",
        'LoKi_nTTClusters': "CONTAINS('Raw/TT/Clusters')",
        'LoKi_nOThits': "CONTAINS('Raw/OT/Times')"
    }

    tuple_seq = SelectionSequence('{}_SelSeq'.format(name), tuple_selection)

    if is_mc:
        # Add MC tuple tools
        mctruth = dtt.addTupleTool('TupleToolMCTruth')
        mctruth.ToolList = [
            'MCTupleToolKinematic',
            'MCTupleToolHierarchy',
            'MCTupleToolPID'
        ]

    return tuple_seq.sequence()


def mc_tuple_maker(name, decay, branches):
    """Return a configured MCDecayTreeTuple instance."""
    dtt = MCDecayTreeTuple('{}_MCTuple'.format(name))
    dtt.Decay = decay
    dtt.TupleName = 'MCTuple'
    dtt.ToolList += [
        'MCTupleToolKinematic',
        'TupleToolEventInfo',
        'MCTupleToolHierarchy',
        'MCTupleToolPrimaries',
        'MCTupleToolPID'
    ]
    dtt.addBranches(branches)

    return dtt


def tuple_sequence():
    """Return the sequencer used for running tuple algorithms.

    The sequencer is configured such that all members are run, as their filter
    flags are ignored.
    """
    seq = GaudiSequencer('TupleSeq')
    seq.IgnoreFilterPassed = True

    return seq
