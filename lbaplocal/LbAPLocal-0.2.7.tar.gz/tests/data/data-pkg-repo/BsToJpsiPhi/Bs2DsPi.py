import os
from Configurables import (
    TupleToolDecayTreeFitter,
    TriggerTisTos,
    GaudiSequencer,
    CheckPV,
    TrackScaleState, TrackSmearState,
    DecayTreeTuple, TupleToolTISTOS, TupleToolGeometry,
    TupleToolDecay, TupleToolPid, TupleToolRecoStats,
    LoKi__Hybrid__TupleTool,
    TupleToolTagging,
    DaVinci,
    BTaggingTool,
    FilterDesktop
)
from FlavourTagging.Tunings import applyTuning as applyFTTuning

# Trigger lines
l0_lines = [
    'L0DiMuonDecision',
    'L0GlobalDecision'
    ]
hlt1_lines = [
     'Hlt1GlobalDecision',
     'Hlt1TrackMuonDecision',
     'Hlt1TrackMVADecision',
     'Hlt1TwoTrackMVADecision',
     'Hlt1B2PhiPhi_LTUNBDecision'
    ]
hlt2_lines = [
    'Hlt2Topo2BodyBBDTDecision',
    'Hlt2Topo3BodyBBDTDecision',
    'Hlt2Topo4BodyBBDTDecision',
    'Hlt2Topo2BodyDecision',
    'Hlt2Topo3BodyDecision',
    'Hlt2Topo4BodyDecision',
    'Hlt2IncPhiSidebandsDecision',
    'Hlt2PhiIncPhiDecision',
    'Hlt2PhiBs2PhiPhiDecision'
    ]
mtl = l0_lines + hlt1_lines + hlt2_lines


is_mc = DaVinci().Simulation
is_mdst = DaVinci().InputType.upper() == 'MDST'
oldline = False if DaVinci().DataType=='2018' else True
line = 'BetaSBs2DsPiDetachedLine' if oldline==False else 'B02DPiD2HHHBeauty2CharmLine'
tes_root = '/Event/AllStreams' if is_mc else '/Event/BhadronCompleteEvent'
if is_mdst:
    DaVinci().RootInTES = tes_root
location = 'Phys/{}/Particles'.format(line)
if not is_mdst:
    location = os.path.join(tes_root, location)
tuple = DecayTreeTuple('Bs2DsPi_Tuple')
tuple.Inputs = [location]
# Unit
SeqPhys = GaudiSequencer('SeqPhys')

if oldline:
    tuple.Decay = '[B0 -> ^(D- -> ^K- ^pi- ^K+) ^pi+]CC'
    tuple.Branches = {
        'B' : '[B0 ->  (D- ->  K-  pi-  K+)  pi+]CC',
        'Ds': '[B0 -> ^(D- ->  K-  pi-  K+)  pi+]CC',
        'hminus': '[B0 ->  (D- -> ^K-  pi-  K+)  pi+]CC',
        'piminus': '[B0 ->  (D- ->  K- ^pi-  K+)  pi+]CC',
        'hplus': '[B0 ->  (D- ->  K-  pi- ^K+)  pi+]CC',
        'piplus': '[B0 ->  (D- ->  K-  pi-  K+) ^pi+]CC'
        }
else:
    tuple.Decay = '[B_s0 -> ^(D_s- -> ^K- ^pi- ^K+) ^pi+]CC'
    tuple.Branches = {
        'B': '[B_s0 ->  (D_s- ->  K-  pi-  K+)  pi+]CC',
        'Ds': '[B_s0 -> ^(D_s- ->  K-  pi-  K+)  pi+]CC',
        'hminus': '[B_s0 ->  (D_s- -> ^K-  pi-  K+)  pi+]CC',
        'piminus': '[B_s0 ->  (D_s- ->  K- ^pi-  K+)  pi+]CC',
        'hplus': '[B_s0 ->  (D_s- ->  K-  pi- ^K+)  pi+]CC',
        'piplus': '[B_s0 ->  (D_s- ->  K-  pi-  K+) ^pi+]CC'
        }

# TupleToolDecay
names = ['B', 'Ds', 'hminus', 'piminus', 'hplus', 'piplus']
for particle in names:
   tuple.addTool(TupleToolDecay, name=particle)

# Tool list
tl= [
    'TupleToolAngles',
    'TupleToolKinematic',
    'TupleToolPid',
    'TupleToolTrackInfo',
    'TupleToolPrimaries',
    'TupleToolPropertime',
    'TupleToolEventInfo',
    'TupleToolRecoStats',
    'TupleToolGeometry',
    'TupleToolTISTOS'
    ]
if is_mc:
    tl += ['TupleToolMCTruth',
           'TupleToolMCBackgroundInfo']

tuple.ToolList += tl
# Refit
tuple.ReFitPVs = True

#Geo
TupleToolGeometry = TupleToolGeometry('TupleToolGeometry')
TupleToolGeometry.RefitPVs = True
TupleToolGeometry.Verbose = True
tuple.addTool(TupleToolGeometry)

# Loki
LoKi_B = LoKi__Hybrid__TupleTool('LoKi_B')
LoKi_B.Variables = {
    'ETA': 'ETA',
    'LOKI_FDCHI2': 'BPVVDCHI2',
    'LOKI_FDS': 'BPVDLS',
    'LOKI_DIRA': 'BPVDIRA',
    'LOKI_DTF_CTAU': 'DTF_CTAU( 0, True )',
    'LOKI_DTF_CTAUS': 'DTF_CTAUSIGNIFICANCE( 0, True )',
    'LOKI_DTF_CHI2NDOF': 'DTF_CHI2NDOF( True )',
    'LOKI_DTF_CTAUERR': 'DTF_CTAUERR( 0, True )',
    'LOKI_MASS_DsConstr': "DTF_FUN ( M , True , 'D_s-' )",
    'LOKI_DTF_VCHI2NDOF': 'DTF_FUN ( VFASPF(VCHI2/VDOF) , True )'
}
tuple.B.addTool(LoKi_B)
tuple.B.ToolList += ["LoKi::Hybrid::TupleTool/LoKi_B"]

# RecoStats to filling SpdMult, etc
tuple.addTool(TupleToolRecoStats, name='TupleToolRecoStats')
tuple.TupleToolRecoStats.Verbose = True

# Refit with mass constraint
PVFit = TupleToolDecayTreeFitter('PVFit')
PVFit.Verbose = True
PVFit.UpdateDaughters = True
PVFit.constrainToOriginVertex = True

PVFitDs = TupleToolDecayTreeFitter('PVFitDs')
PVFitDs.Verbose = True
PVFitDs.UpdateDaughters = True
PVFitDs.constrainToOriginVertex = True
if oldline:
   PVFitDs.Substitutions = {
       'B0 -> ^(D- -> K- pi- K+) pi+': 'D_s-',
       'B~0-> ^(D+ -> K+ pi+ K-) pi-': 'D_s+'
       }
PVFitDs.daughtersToConstrain = ['D_s-']
tuple.B.addTool(PVFit)
tuple.B.addTool(PVFitDs)
tuple.B.ToolList += ["TupleToolDecayTreeFitter/PVFit"]
tuple.B.ToolList += ["TupleToolDecayTreeFitter/PVFitDs"]

# Trigger
TisTos = TupleToolTISTOS('TisTos')
TisTos.Verbose = True
TisTos.TriggerList = mtl

# Change TOSFracMu for Ds, B
tuple.B.addTool(TisTos)
tuple.B.TisTos.addTool(TriggerTisTos())
tuple.B.ToolList += ['TupleToolTISTOS/TisTos']
tuple.B.TisTos.TriggerTisTos.TOSFracMuon = 0
tuple.B.TisTos.TriggerTisTos.TOSFracEcal = 0
tuple.B.TisTos.TriggerTisTos.TOSFracHcal = 0

# specific tagging tuple tool
PTagging = TupleToolTagging('PTagging')
if is_mdst:
    PTagging.UseFTfromDST = True
else:
    PTagging.Verbose = True
    btagtool = PTagging.addTool(BTaggingTool, name='MyBTaggingTool')

    applyFTTuning(btagtool, tuning_version='Summer2017Optimisation_v4_Run2')
    PTagging.TaggingToolName = btagtool.getFullName()
tuple.B.addTool(PTagging)
tuple.B.ToolList += ['TupleToolTagging/PTagging']

# primary vertex selection
checkpv = CheckPV()
# Require that there are valid PVs after refitting, as required by
# TupleToolPropertime
checkrefitpv = FilterDesktop('CheckRefittedPVs_{}'.format(tuple.name()),
                             Code='BPVVALID()',
                             Inputs=tuple.Inputs,
                             ReFitPVs=True)

# apply momentum scaling for data and momentum smearing for MC
scale_or_smear = TrackSmearState('TrackSmearState') if is_mc else TrackScaleState('TrackScaleState')

SeqPhys.Members += [checkpv, checkrefitpv, scale_or_smear, tuple]
DaVinci().UserAlgorithms = [SeqPhys]
