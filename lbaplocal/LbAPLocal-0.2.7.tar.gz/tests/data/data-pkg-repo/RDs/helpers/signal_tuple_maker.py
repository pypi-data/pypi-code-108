from DecayTreeTuple.Configuration import *
from Gaudi.Configuration import *
from DaVinci.Configuration import *
from PhysConf.Filters import LoKi_Filters
from Configurables import SubstitutePID
from Configurables import DecayTreeTuple, DaVinci,  LoKi__Hybrid__TupleTool, TupleToolDecayTreeFitter, TupleToolTrackIsolation, TupleToolTrigger, TupleToolRecoStats, TupleToolKinematic, TupleToolGeometry,TupleToolVtxIsoln, TupleToolConeIsolation


def addNtupleToDaVinci(isSim, stream, line):

    dtt = DecayTreeTuple('SignalTuple')
    dtt.Decay = "[ (B_s0 -> ^(D_s- -> ^K+ ^K- ^pi-) ^(tau+ -> ^pi+ ^pi- ^pi+ ) ) ]CC"

    dtt.ReFitPVs = True
    dtt.RevertToPositiveID = False

    dtt.addTupleTool("TupleToolPrimaries")
    #dtt.addTupleTool('TupleToolEventInfo')#already included
    dtt.addTupleTool("TupleToolVtxIsoln")

    #dtt.addTool(TupleToolTrackIsolation, name="TupleToolTrackIsolation")
    #dtt.TupleToolTrackIsolation.FillAsymmetry = False ##in philip era True che significa?????
    #dtt.TupleToolTrackIsolation.FillDeltaAngles = False
    #dtt.TupleToolTrackIsolation.MinConeAngle = 1.0

    dtt.addTool(TupleToolConeIsolation, name="TupleToolConeIsolation")
    dtt.TupleToolConeIsolation.ExtraParticlesLocation = 'Phys/StdAllNoPIDsPions/Particles'
    dtt.TupleToolConeIsolation.FillPi0Info = True
    dtt.TupleToolConeIsolation.MaxConeSize = 1.0


    #dtt.addTupleTool("TupleToolGeometry") #already included
    dtt.addTool( TupleToolGeometry, name = "TupleToolGeometry" )
    #dtt.TupleToolGeometry.OutputLevel = DEBUG
    dtt.TupleToolGeometry.Verbose = True
    dtt.TupleToolGeometry.RefitPVs = True
    dtt.TupleToolGeometry.FillMultiPV = True
    
    dtt.addTupleTool("TupleToolRecoStats")
    dtt.addTool(TupleToolRecoStats, name="TupleToolRecoStats")
    dtt.TupleToolRecoStats.Verbose = False

    dtt.addTupleTool("TupleToolTrackInfo") # ghostProb


    dtt.addBranches ({
        "B" : "^([ (B_s0 -> (D_s- -> K+ K- pi-) (tau+ -> pi+ pi- pi+  ) ) ]CC)",
        "Y" : "[ (B_s0 -> (D_s- -> K+ K- pi-) ^(tau+ -> pi+ pi- pi+  ) ) ]CC",
        "p1_fromY" : "[ (B_s0 -> (D_s- -> K+ K- pi-) (tau+ -> ^pi+ pi- pi+  ) ) ]CC",
        "p2_fromY" : "[ (B_s0 -> (D_s- -> K+ K- pi-) (tau+ -> pi+ ^pi- pi+  ) ) ]CC",
        "p3_fromY" : "[ (B_s0 -> (D_s- -> K+ K- pi-) (tau+ -> pi+ pi- ^pi+  ) ) ]CC",
        "Xc" : "[ (B_s0 -> ^(D_s- -> K+ K- pi-) (tau+ -> pi+ pi- pi+  ) ) ]CC",
        "p1_fromXc" : "[ (B_s0 -> (D_s- -> ^K+ K- pi-) (tau+ -> pi+ pi- pi+  ) ) ]CC",
        "p2_fromXc" : "[ (B_s0 -> (D_s- -> K+ ^K- pi-) (tau+ -> pi+ pi- pi+  ) ) ]CC",
        "p3_fromXc" : "[ (B_s0 -> (D_s- -> K+ K- ^pi-) (tau+ -> pi+ pi- pi+  ) ) ]CC"
    })

    tlist=["L0HadronDecision", "L0GlobalDecision",
           "Hlt1GlobalDecision","Hlt1TrackAllL0Decision","Hlt1TrackAllL0TightDecision",      #### AGGIUNTO
           ####"Hlt1TrackMVADecision","Hlt1TwoTrackMVADecision", # Non c'e' nel Run1
           "Hlt2GlobalDecision",
           "Hlt2Topo2BodyBBDTDecision","Hlt2Topo3BodyBBDTDecision" ,"Hlt2Topo4BodyBBDTDecision" ,
           "Hlt2Topo2BodySimpleDecision","Hlt2Topo3BodySimpleDecision","Hlt2Topo4BodySimpleDecision",
           "Hlt2IncPhiDecision","Hlt2IncPhiSidebandsDecision",
           "Hlt2CharmHadD2HHHDecision", "Hlt2CharmHadD2HHHWideMassDecision",  ### Non c'e'
           ]
    ########### ADDITIONAL Trigger info
    # 1. To get information about the TCK
    # dtt.addTupleTool("TupleToolEventInfo")
    # 2. To get information about trigger decisions
    ttt = dtt.addTupleTool("TupleToolTrigger")
    ttt.Verbose = True #Needed to get trigger decisions
    ttt.TriggerList = tlist

    #######################
    dtt.addTool(TupleToolDecay, name="B")

    #dttBt = dtt.B.addTool(TupleToolTrigger)
    #dttBt.TupleToolTrigger.Verbose = True
    #dttBt.TupleToolTrigger.TriggerList = tlist

    dttB = dtt.B.addTupleTool('TupleToolTISTOS')
    dttB.VerboseL0=True
    dttB.VerboseHlt1=True
    dttB.VerboseHlt2=True
    dttB.TriggerList = tlist

    from Configurables import MCMatchObjP2MCRelator
    
    if (isSim):
        dtt.ToolList +=  [
            "TupleToolMCBackgroundInfo",
            #"TupleToolPhotonInfo"
            ]
        
        # Add TupleToolMCTruth with fix for "Fatal error No valid data at '/Event/Hlt2/Long/Protos'"
        #default_rel_locs = MCMatchObjP2MCRelator().getDefaultProperty('RelTableLocations')
        #rel_locs = [loc for loc in default_rel_locs if 'Turbo' not in loc]
        
        mctruth = dtt.addTupleTool('TupleToolMCTruth')
        mctruth.ToolList =  [
            "MCTupleToolHierarchy",
	    "MCTupleToolKinematic"
            ]
        #mctruth.addTool(MCMatchObjP2MCRelator)
        #mctruth.MCMatchObjP2MCRelator.RelTableLocations = rel_locs


    LoKiTool= dtt.addTupleTool("LoKi::Hybrid::TupleTool/LoKiTool")
    LoKiTool.Variables = { "ETA" : "ETA" }

    dtt.B.addTupleTool('TupleToolDecayTreeFitter/DTF_Kpipi')
    dtt.B.DTF_Kpipi.constrainToOriginVertex = False
    dtt.B.DTF_Kpipi.Verbose = False
    dtt.B.DTF_Kpipi.Substitutions = {
    'Beauty -> Charm (tau+ -> ^pi+ pi- pi+ ) ': 'K+',
    'Beauty -> Charm (tau- -> ^pi- pi+ pi- ) ': 'K-',
    'Beauty -> X+ ^(Charm & X-)': 'D_s-',
    'Beauty -> X- ^(Charm & X+)': 'D_s+'}
    dtt.B.DTF_Kpipi.daughtersToConstrain = ["D_s-", "D_s+" ]
    dtt.B.DTF_Kpipi.UpdateDaughters = False

    dtt.B.addTupleTool('TupleToolDecayTreeFitter/DTF_piKpi')
    dtt.B.DTF_piKpi.constrainToOriginVertex = False
    dtt.B.DTF_piKpi.Verbose = False
    dtt.B.DTF_piKpi.Substitutions = {
    'Beauty -> Charm (tau+ -> pi+ ^pi- pi+ ) ': 'K-',
    'Beauty -> Charm (tau- -> pi- ^pi+ pi- ) ': 'K+',
    'Beauty -> X+ ^(Charm & X-)': 'D_s-',
    'Beauty -> X- ^(Charm & X+)': 'D_s+'}
    dtt.B.DTF_piKpi.daughtersToConstrain = ["D_s-", "D_s+" ]
    dtt.B.DTF_piKpi.UpdateDaughters = False

    dtt.B.addTupleTool('TupleToolDecayTreeFitter/DTF_pipiK')
    dtt.B.DTF_pipiK.constrainToOriginVertex = False
    dtt.B.DTF_pipiK.Verbose = False
    dtt.B.DTF_pipiK.Substitutions = {
    'Beauty -> Charm (tau+ -> pi+ pi- ^pi+ ) ': 'K+',
    'Beauty -> Charm (tau- -> pi- pi+ ^pi- ) ': 'K-',
    'Beauty -> X+ ^(Charm & X-)': 'D_s-',
    'Beauty -> X- ^(Charm & X+)': 'D_s+'}
    dtt.B.DTF_pipiK.daughtersToConstrain = ["D_s-", "D_s+" ]
    dtt.B.DTF_pipiK.UpdateDaughters = False



    dtt.B.addTool(TupleToolDecayTreeFitter("DTF"))
    dtt.B.ToolList +=  ["TupleToolDecayTreeFitter/DTF" ]
    dtt.B.DTF.constrainToOriginVertex = False
    dtt.B.DTF.Substitutions = { 'Beauty -> X+ ^(Charm & X-)' : 'D_s-', 'Beauty -> X- ^(Charm & X+)' : 'D_s+'  }
    dtt.B.DTF.daughtersToConstrain = ["D_s-", "D_s+", ]
    dtt.B.DTF.UpdateDaughters = True
    dtt.B.DTF.Verbose = True
    
    dtt.B.addTool(TupleToolDecayTreeFitter("DTFPVDs"))
    dtt.B.ToolList +=  ["TupleToolDecayTreeFitter/DTFPVDs" ]
    dtt.B.DTFPVDs.constrainToOriginVertex = True
    dtt.B.DTFPVDs.Substitutions = { 'Beauty -> X+ ^(Charm & X-)' : 'D_s-', 'Beauty -> X- ^(Charm & X+)' : 'D_s+' }
    dtt.B.DTFPVDs.daughtersToConstrain = ["D_s-", "D_s+" ]
    dtt.B.DTFPVDs.UpdateDaughters = True
    dtt.B.DTFPVDs.Verbose = True


    LoKiToolB=dtt.B.addTupleTool("LoKi::Hybrid::TupleTool/LoKiToolB")
    LoKiToolB.Variables = {
        "DOCA1" : "DOCA(1,2)",
        "TAU" : "BPVLTIME()",
        "TAUERR" : "BPVLTERR()" }

    dtt.addTool(TupleToolDecay, name="Xc")
    LoKiToolXc = dtt.Xc.addTupleTool("LoKi::Hybrid::TupleTool/LoKiToolXc")
    LoKiToolXc.Variables = { "DOCA1" : "DOCA(1,2)" , "DOCA2" : "DOCA(1,3)" , "DOCA3" : "DOCA(2,3)"}

    dtt.addTool(TupleToolDecay, name="Y")
    LoKiToolY = dtt.Y.addTupleTool("LoKi::Hybrid::TupleTool/LoKiToolY")
    LoKiToolY.Variables = { "DOCA1" : "DOCA(1,2)" , "DOCA2" : "DOCA(1,3)" , "DOCA3" : "DOCA(2,3)" }

    #dttXct = dtt.Xc.addTool(TupleToolTrigger)
    #dttXct.TupleToolTrigger.Verbose = True
    #dttXct.TupleToolTrigger.TriggerList = tlist

    dttXc = dtt.Xc.addTupleTool('TupleToolTISTOS')
    dttXc.VerboseL0=True
    dttXc.VerboseHlt1=True
    dttXc.VerboseHlt2=True
    dttXc.TriggerList= tlist

    
    # For 2018 data the line is explained here:
    # http://lhcbdoc.web.cern.ch/lhcbdoc/stripping/config/stripping34/bhadroncompleteevent/strippingbs2dstaunuforb2xtaunualllines.html
    # if isSim:
    #     stream = 'RXcHad.Strip'
    #     #stream = 'AllStreams'  #### MC di fondo non filtrato
    #     #line = 'Bs2DsTauNuForB2XTauNu'   # segnale
    #     #line = 'Bs2DsTauNuForB2XTauNuAllLines'   # segnale    
    #     line = line_name
    #     dtt.Inputs = ['/Event/{0}/Phys/{1}/Particles'.format(stream, line)]
    # else:
    #     stream = 'BhadronCompleteEvent'
    #     #stream = 'RXcHad.Strip'
    #     line = 'Bs2DsTauNuForB2XTauNu'
    #     dtt.Inputs = ['/Event/{0}/Phys/{1}/Particles'.format(stream,line)]

    # Setting the input based on the parameters passed
    dtt.Inputs = ['/Event/{0}/Phys/{1}/Particles'.format(stream,line)]

    # Configure DaVinci
    DaVinci().UserAlgorithms += [dtt]

