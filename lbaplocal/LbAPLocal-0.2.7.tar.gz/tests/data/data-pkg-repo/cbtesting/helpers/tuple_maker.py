import os

from Configurables import (
    DaVinci,
    GaudiSequencer,
    DecayTreeTuple,
    MCDecayTreeTuple,
    TupleToolDecay
)

from PhysSelPython.Wrappers import (
    AutomaticData,
    FilterSelection,
    SelectionSequence,
)
from DecayTreeTuple.Configuration import *

from related_info import getLoKiTool
import tags
import locations
from cbtesting.helpers import decay_descriptors 

def tuple_maker(tuple_name,upstream_electrons):
    """Return a sequence for producing ntuples.

    Assumes the decay structure is like:

        Beauty -> (J/Psi -> l- l+) (Lambda0 -> p pi-)
    """
    # FIRST OBTAIN SOME INFORMATION FROM DAVINCI
    year = DaVinci().DataType
    is_mc = DaVinci().Simulation
    is_mdst = (DaVinci().InputType.upper() == 'MDST')

    # NOW DETERMINE STREAM NAME
    # The sample name is formatted as {year}_{polarity}_MC_{decay}  ; needed for stripping line names
    if is_mc:
        sample_decay   = DaVinci().TupleFile
        #decay = 'Lb2LJpsmm' # THIS WAS USED ONLY FOR TESTING BY HAND 
        sample_name = year+"_MagUp" # Note that polarity does not matter for line name
        print("TEST ", sample_decay)
        if is_mc:     sample_name += "_MC_"+sample_decay 
    else:
        sample_name = None # Sample name not needed for Data

    print("Test2 ", sample_name) 
    # Determine stream and set tags if needed
    if is_mc:     
        sample_settings = tags.tags[sample_name]
        stream = sample_settings['StrippingStream']
        DaVinci().CondDBtag = sample_settings['conddb']
        DaVinci().DDDBtag   = sample_settings['dddb']
    if not is_mc: 
        stream = 'Leptonic'

    # NOW DETERMINE STRIPPING LINE
    # Get which two leptons are in final state
    # tuple_name definitions are Lb2JpsiL_llTuple, Lb2LemuTuple,Bu2JpsiK_llTuple,Lb2Lee_SSTuple  
    # so replace Lb2L by _, split at '_', take second part and slice first two particles
    # this returns mm, ee or em; 
    lepton_mode = tuple_name.replace('Lb2L','_').split('_')[1][:2]
    if 'em' in lepton_mode: lepton_mode = 'me' #need 'me' for stripping line name
    if 'SS' in tuple_name:  lepton_mode += 'SS'

    print ('Lepton_mode',lepton_mode)

    # Combine stream and stripping line name depending on case to return locations
    location_list = locations.get_locations(stream,lepton_mode,sample_name,is_mc,is_mdst,upstream_electrons=upstream_electrons)    
    print(location_list)

    # FOR LOADING DECAY DESCRIPTORS, SETTING BRANCHES, ETC.
    decay_rec                 = tuple_name.replace('Tuple','') # DECAY NAME
    decay_desc_full           = decay_descriptors.dict_rec[decay_rec]
    tuple_branches, part_list = decay_descriptors.tuple_branches(decay_desc_full)
    print ('Decay rec',decay_rec)   
    print ('Decay desc',decay_desc_full)   
    
    dtt = DecayTreeTuple(tuple_name)
    dtt.Inputs = location_list
    dtt.Decay  = decay_desc_full
     


    dtt.addBranches(tuple_branches)

    
    # OBTAIN PARTICLE NAMES FOR ASSIGNING TUPLETOOLS 
    if 'Lb' in decay_rec:    
        b_hadr     = [dtt.Lb]
        resonances = [dtt.JPs,dtt.L0]
        hadrons    = [dtt.P ,dtt.Pi]
        leptons    = [dtt.L1,dtt.L2]  
        dtf_parts  = ['Lambda_b0','Lambda0']
        dtf_label  = ['Lb'       ,'L0'     ]

    if 'Bd' in decay_rec:    
        b_hadr     = [dtt.B]
        resonances = [dtt.JPs,dtt.K0]
        hadrons    = [dtt.Pi1,dtt.Pi2]
        leptons    = [dtt.L1,dtt.L2]  
        dtf_parts  = ['B0'       ,'KS0'    ]
        dtf_label  = ['B0'       ,'K0'     ]

    if 'Bu' in decay_rec:
        b_hadr     = [dtt.B]
        resonances = [dtt.JPs]
        hadrons    = [dtt.K]
        leptons    = [dtt.L1,dtt.L2]  
        dtf_parts  = ['B+']
        dtf_label  = ['B']

    

    particles  = b_hadr+resonances+hadrons+leptons    
    print (b_hadr[0])
    print (particles[0])
    print (b_hadr==particles[0])


    # NOTE: DEFAULT TOOLS INCLUDED ALWAYS so this is just included for documentation
    default_tools = [
        "TupleToolANNPID",
        "TupleToolGeometry",
        "TupleToolPid",
        "TupleToolEventInfo",
        #"TupleToolKinematic",
        ]
    # Tool list
    specific_tools = [
        "TupleToolPropertime",
    ]
    event_wide_tools = [
        "TupleToolL0Data",
        "TupleToolPrimaries",
        "TupleToolRecoStats",
        "TupleToolTrackInfo",
    ]
   
    for particle in particles:
        kin_tool = particle.addTupleTool("TupleToolKinematic")
        kin_tool.Verbose = True # To include AtVtx_P, which gives better resolution for DD tracks

    for tool in specific_tools:
        for particle in particles:
            particle.addTupleTool(tool)
    for tool in event_wide_tools:
        dtt.addTupleTool(tool)

    # Trigger lines
    l0_triggers = ["L0HadronDecision", "L0ElectronDecision",
                   'L0MuonDecision','L0DiMuonDecision','L0PhotonDecision']

    hlt1_muon       = [ "Hlt1TrackMuonDecision", "Hlt1SingleMuonDecision" ,
                        "Hlt1SingleMuonHighPTDecision" ]
    hlt1_muon_run2  = [ "Hlt1TrackMuonMVADecision"]
    hlt1_dimuon     = [ "Hlt1DiMuonHighMassDecision"    ]
 
    hlt1_track_run1 = [ "Hlt1TrackAllL0Decision", "Hlt1TrackAllL0TightDecision" ]
    hlt1_track_run2 = [ "Hlt1TrackMVADecision", "Hlt1TrackMVALooseDecision",
                        "Hlt1TwoTrackMVADecision", "Hlt1TwoTrackMVALooseDecision"]

    hlt2_muon       = ["Hlt2SingleMuonDecision"]
    hlt2_electron  = ["Hlt2SingleElectronTFHighPtDecision",
                       "Hlt2SingleElectronTFLowPtDecision"]
    hlt2_dimuon     = [ "Hlt2DiMuonDetachedDecision", "Hlt2DiMuonDetachedHeavyDecision",
            "Hlt2DiMuonDetachedJPsiDecision", "Hlt2DiMuonDetachedPsi2SDecision",
            "Hlt2DiMuonJPsiHighPTDecision", "Hlt2DiMuonPsi2SHighPTDecision"         ]

    hlt2_topo_run1  = [ "Hlt2Topo2BodyBBDTDecision", "Hlt2Topo3BodyBBDTDecision"]
    #            "Hlt2Topo4BodyBBDTDecision"]
    hlt2_topomu_run1   = [line.replace('Topo','TopoMu'   ) for line in hlt2_topo_run1]
    hlt2_topoe_run1    = [line.replace('Topo','TopoE'    ) for line in hlt2_topo_run1]
    hlt2_topo_run2     = [line.replace('BBDT',''         ) for line in hlt2_topo_run1]
    hlt2_topomu_run2   = [line.replace('Topo','TopoMu'   ) for line in hlt2_topo_run2]
    hlt2_topoe_run2    = [line.replace('Topo','TopoE'    ) for line in hlt2_topo_run2]
    hlt2_topomumu_run2 = [line.replace('Topo','TopoMuMu' ) for line in hlt2_topo_run2]
    hlt2_topoee_run2   = [line.replace('Topo','TopoEE'   ) for line in hlt2_topo_run2]
    hlt2_topoemu_run2  = [line.replace('Topo','TopoMuE'  ) for line in hlt2_topo_run2]

     # L0 lines
    from Configurables import TupleToolTISTOS
    for (i,particle) in enumerate(particles):
        particle.addTool( TupleToolTISTOS, name = "L0TISTOS"+str(i) )
        particle.ToolList += [ "TupleToolTISTOS/L0TISTOS"+str(i) ]

        # Hlt1 info for each particle to calibrate TrackMVA
        particle.addTool( TupleToolTISTOS, name = "HltTISTOS"+str(i) )
        particle.ToolList += [ "TupleToolTISTOS/HltTISTOS"+str(i) ]

    L0TISTOS_list = [ particles[0].L0TISTOS0,particles[1].L0TISTOS1,particles[2].L0TISTOS2,particles[3].L0TISTOS3,particles[4].L0TISTOS4, ]
    if len(particles) == 7: L0TISTOS_list += [particles[5].L0TISTOS5, particles[6].L0TISTOS6 ]
    HltTISTOS_list = [ particles[0].HltTISTOS0,particles[1].HltTISTOS1,particles[2].HltTISTOS2,particles[3].HltTISTOS3,particles[4].HltTISTOS4, ]
    if len(particles) == 7: HltTISTOS_list += [particles[5].HltTISTOS5, particles[6].HltTISTOS6 ]

    for (i,particle) in enumerate(particles):
        L0TISTOS_list[i].TriggerList = l0_triggers 
        L0TISTOS_list[i].Verbose = True



        # Start with empty list
        HltTISTOS_list[i].TriggerList = []

        # Add the correct trigger lines for the year and channel
        if year in ['2011', '2012']:
            HltTISTOS_list[i].TriggerList += hlt1_track_run1
        else:
            HltTISTOS_list[i].TriggerList += hlt1_track_run2            

        HltTISTOS_list[i].Verbose = True

        if particle in particles[:2]+particles[-2:]: # For Lb, Jpsi, and leptons
            if 'm' in lepton_mode:
                HltTISTOS_list[i].TriggerList += hlt1_muon+hlt2_muon
                if year in ['2016', '2017', '2018']:
                    HltTISTOS_list[i].TriggerList += hlt1_muon_run2
            if 'e' in lepton_mode:
                HltTISTOS_list[i].TriggerList += hlt2_electron

        if particle in particles[:2]: # For Lb and Jpsi
            # For all years
            if 'mm' in lepton_mode:
                HltTISTOS_list[i].TriggerList += hlt1_dimuon
                HltTISTOS_list[i].TriggerList += hlt2_dimuon

            # Add the correct trigger lines based per year and decay channel
            if year in ['2011', '2012']:
                HltTISTOS_list[i].TriggerList += hlt2_topo_run1
                if 'm' in lepton_mode:
                    HltTISTOS_list[i].TriggerList += hlt2_topomu_run1
                if 'e' in lepton_mode:
                    HltTISTOS_list[i].TriggerList += hlt2_topoe_run1

            else:  
                HltTISTOS_list[i].TriggerList += hlt2_topo_run2

                # 2016, 2017, 2018 specific
                if year in ['2016','2017','2018']:
                    if 'mm' in lepton_mode:
                        HltTISTOS_list[i].TriggerList += hlt2_topomu_run2+hlt2_topomumu_run2
                    if 'me' in lepton_mode: 
                        HltTISTOS_list[i].TriggerList += hlt2_topomu_run2+hlt2_topoe_run2+hlt2_topoemu_run2
                    if 'ee' in lepton_mode:
                        HltTISTOS_list[i].TriggerList += hlt2_topoe_run2+hlt2_topoee_run2 



    # Include TupleToolL0Calo for correction of ET cut in 2016 samples + possibility to bin in CaloRegions
    from Configurables import TupleToolL0Calo
    for particle in leptons+hadrons: 
        particle.addTool(TupleToolL0Calo,name='L0Calo_HCAL')
        particle.ToolList += [ "TupleToolL0Calo/L0Calo_HCAL"]
        particle.L0Calo_HCAL.WhichCalo = "HCAL"

    for particle in leptons+hadrons:
        particle.addTool(TupleToolL0Calo,name='L0Calo_ECAL')
        particle.ToolList += [ "TupleToolL0Calo/L0Calo_ECAL"]
        particle.L0Calo_ECAL.WhichCalo = "ECAL"

    # Different DecayTreeFitter setups
    from Configurables import TupleToolDecayTreeFitter
    dtf_name_bhad_pv = "DTF_{0}_PV".format(dtf_label[0]) 

    particles[0].addTool( TupleToolDecayTreeFitter, name = "DTF" )
    particles[0].ToolList += [ "TupleToolDecayTreeFitter/DTF" ]

    particles[0].addTool( particles[0].DTF.clone( "DTF_PV",
                                          Verbose = True,
                                          constrainToOriginVertex = True ) )
    particles[0].ToolList += [ "TupleToolDecayTreeFitter/DTF_PV" ]

    particles[0].addTool( particles[0].DTF.clone( dtf_name_bhad_pv,
                                          Verbose = True,
                                          constrainToOriginVertex = True,
                                          daughtersToConstrain = [dtf_parts[0]] ) )
    particles[0].ToolList += [ "TupleToolDecayTreeFitter/"+dtf_name_bhad_pv ]

    psi2s_sub =  {tuple_branches['JPs']:"psi(2S)"}

    if len(dtf_label) == 2:
        dtf_name_hadr_pv = "DTF_{0}_PV".format(dtf_label[1]) 
        dtf_name_bhad_hadr_pv = "DTF_{0}_{1}_PV".format(dtf_label[0],dtf_label[1]) 
        dtf_name_hadr_jpsi_pv = "DTF_{0}_JPs_PV".format(dtf_label[1]) 
        dtf_name_hadr_psi_pv = "DTF_{0}_Psi_PV".format(dtf_label[1]) 
       
        particles[0].addTool( particles[0].DTF.clone( dtf_name_hadr_pv,
                                              Verbose = True,
                                              constrainToOriginVertex = True,
                                              daughtersToConstrain = [dtf_parts[1]] ) )
        particles[0].ToolList += [ "TupleToolDecayTreeFitter/"+dtf_name_hadr_pv]

        particles[0].addTool( particles[0].DTF.clone( dtf_name_bhad_hadr_pv,
                                              Verbose = True,
                                              constrainToOriginVertex = True,
                                              daughtersToConstrain = dtf_parts ) )
        particles[0].ToolList += [ "TupleToolDecayTreeFitter/"+dtf_name_bhad_hadr_pv ]


        particles[0].addTool( particles[0].DTF.clone( dtf_name_hadr_jpsi_pv,
                                              Verbose = True,
                                              constrainToOriginVertex = True,
                                              daughtersToConstrain = [dtf_parts[1]]+["J/psi(1S)" ] ) )
        particles[0].ToolList += [ "TupleToolDecayTreeFitter/"+dtf_name_hadr_jpsi_pv ]

        particles[0].addTool( particles[0].DTF.clone( dtf_name_hadr_psi_pv,
                                              Verbose = True,
                                              constrainToOriginVertex = True,
                                              daughtersToConstrain = [dtf_parts[1]]+["psi(2S)" ],
                                              Substitutions = psi2s_sub) )
        particles[0].ToolList += [ "TupleToolDecayTreeFitter/"+dtf_name_hadr_psi_pv ]

    else:
        dtf_name_hadr_jpsi_pv = 'DTF_JPs_PV'
        dtf_name_hadr_psi_pv  = 'DTF_Psi_PV'

        particles[0].addTool( particles[0].DTF.clone( dtf_name_hadr_jpsi_pv,
                                              Verbose = True,
                                              constrainToOriginVertex = True,
                                              daughtersToConstrain = ["J/psi(1S)" ] ) )
        particles[0].ToolList += [ "TupleToolDecayTreeFitter/"+dtf_name_hadr_jpsi_pv ]

        particles[0].addTool( particles[0].DTF.clone( dtf_name_hadr_psi_pv,
                                              Verbose = True,
                                              constrainToOriginVertex = True,
                                              daughtersToConstrain = ["psi(2S)" ],
                                              Substitutions = psi2s_sub ) )
        particles[0].ToolList += [ "TupleToolDecayTreeFitter/"+dtf_name_hadr_psi_pv ]


    # Adding hop from loki functor
    from Configurables import  LoKi__Hybrid__TupleTool
    LoKi_HOP = LoKi__Hybrid__TupleTool("LoKi_HOP")
    LoKi_HOP.Variables ={
        'hop_LoKi_mass_bv': 'BPVHOPM()',
        'hop_LoKi_mass': 'HOPM(0,0,0)',
                }

    if 'e' in lepton_mode:
        particles[0].ToolList += [ "LoKi::Hybrid::TupleTool/LoKi_HOP" ]
        particles[0].addTool(LoKi_HOP)

    # Adding MIPCHI2 variable to p and pi
    LoKi_MIPCHI2 = LoKi__Hybrid__TupleTool("LoKi_MIPCHI2DV")
    LoKi_MIPCHI2.Variables ={
        "MIPCHI2" : "MIPCHI2DV(PRIMARY)",
                }

    # Adding Track momenta to l1 and l2
    LoKi_Track_mom = LoKi__Hybrid__TupleTool("LoKi_Track_mom")
    LoKi_Track_mom.Variables ={
        "TRACK_P"  : "PPINFO(504,-100,-200)",
        "TRACK_PT" : "PPINFO(505,-100,-200)",
        "TRACK_PX" : "PPINFO(505,-1e7,-1e7) * cos( PHI )",
        "TRACK_PY" : "PPINFO(505,-1e7,-1e7) * sin( PHI )",
        "TRACK_PZ" : "PPINFO(505,-1e7,-1e7) * sinh(ETA )",
                }

    #adding DOCA variables
    LoKi_DOCA = LoKi__Hybrid__TupleTool("LoKi_DOCA")
    LoKi_DOCA.Variables = {
        "DOCA01"  :  "DOCA(0,1)",
        "DOCA02"  :  "DOCA(0,2)",
        "DOCA12"  :  "DOCA(1,2)",
        "DOCA_MAX":  "DOCAMAX",
        }

    LoKi_ACC = LoKi__Hybrid__TupleTool("LoKi_ACC")
    LoKi_ACC.Variables = {
        "InAccSpd"  : "PPINFO( LHCb.ProtoParticle.InAccSpd,  -1 )",
        "InAccPrs"  : "PPINFO( LHCb.ProtoParticle.InAccPrs,  -1 )",
        "InAccEcal" : "PPINFO( LHCb.ProtoParticle.InAccEcal, -1 )",
        "InAccHcal" : "PPINFO( LHCb.ProtoParticle.InAccHcal, -1 )",
        "InAccMuon" : "PPINFO( LHCb.ProtoParticle.InAccMuon, -1 )",
        "ETA" : "ETA",
        "PHI" : "PHI"
        }

    for lept in leptons:
        lept.ToolList += [ "LoKi::Hybrid::TupleTool/LoKi_Track_mom" ]
        lept.addTool(LoKi_Track_mom)
        if 'e' in lepton_mode:
            lept.ToolList += ["TupleToolBremInfo"]

    for hadr in hadrons:
        hadr.ToolList += [ "LoKi::Hybrid::TupleTool/LoKi_MIPCHI2DV" ]
        hadr.addTool(LoKi_MIPCHI2)

    for res in resonances:
        res.ToolList += [ "LoKi::Hybrid::TupleTool/LoKi_DOCA"]
        res.addTool(LoKi_DOCA)

    for part in leptons+hadrons:
        part.ToolList += [ "LoKi::Hybrid::TupleTool/LoKi_ACC" ]
        part.addTool(LoKi_ACC)

    # Code by Maarten to include all kinds of q2 variables
    ep_pt = "CHILD(1, CHILD(1, PPINFO(505,-100,-200)))"
    em_pt = "CHILD(1, CHILD(2, PPINFO(505,-100,-200)))"
    ep_eta = "CHILD(1, CHILD(1, ETA))"
    em_eta = "CHILD(1, CHILD(2, ETA))"
    ep_phi = "CHILD(1, CHILD(1, PHI))"
    em_phi = "CHILD(1, CHILD(2, PHI))"

    
    particles[0].addTupleTool('LoKi::Hybrid::TupleTool/q2vars')
    particles[0].q2vars.Variables = { 
                               "q2"              : "(MAXTREE('J/psi(1S)'==ABSID,M)/GeV)**2" 
                             , "q2_nobrem"       : "(2.0*{0}*{1}*(cosh({2}-{3})-cos({4}-{5})))/((GeV)**2)".format(ep_pt,em_pt,ep_eta,em_eta,ep_phi,em_phi) 
                             }

    # Mass substitutions
    from Configurables import TupleToolSubMass
    particles[0].addTool( TupleToolSubMass )
    particles[0].ToolList += [ "TupleToolSubMass" ]
    particles[0].TupleToolSubMass.EndTreePIDs = [22]

    particles[0].TupleToolSubMass.Substitution       += [ "p+ => pi+" ]
    particles[0].TupleToolSubMass.Substitution       += [ "p+ => K+" ]
    particles[0].TupleToolSubMass.Substitution       += [ "pi- => p~-" ]
    particles[0].TupleToolSubMass.Substitution       += [ "pi- => K-" ]
    #e/mu for vetoes of ee/mumu resonances, emu swaps, hadronic vetoes 
    particles[0].TupleToolSubMass.DoubleSubstitution += [ "mu+/e- => e+/mu-" ]
    particles[0].TupleToolSubMass.DoubleSubstitution += [ "e+/e- => mu+/mu-" ]
    particles[0].TupleToolSubMass.DoubleSubstitution += [ "mu+/mu- => e+/e-" ]
    particles[0].TupleToolSubMass.DoubleSubstitution += [ "mu+/e- => e+/pi-" ]
    particles[0].TupleToolSubMass.DoubleSubstitution += [ "e+/e- => mu+/pi-" ]
    particles[0].TupleToolSubMass.DoubleSubstitution += [ "mu+/mu-=> e+/pi-" ]
    particles[0].TupleToolSubMass.DoubleSubstitution += [ "mu+/e- => pi+/mu-" ]
    particles[0].TupleToolSubMass.DoubleSubstitution += [ "e+/e- => pi+/mu-" ]
    particles[0].TupleToolSubMass.DoubleSubstitution += [ "mu+/mu- => pi+/e-" ]
    particles[0].TupleToolSubMass.DoubleSubstitution += [ "p+/pi- => pi+/p~-" ] 


    # Adding hop from tuple tool
    from Configurables import TupleToolHOP
    particles[0].addTool(TupleToolHOP, name = "LbHOP")
    particles[0].ToolList += [ "TupleToolHOP/LbHOP"]

    # Add isolation variables
    from Configurables import TupleToolTrackIsolation,TupleToolConeIsolation
    if not is_mdst:
        particles[0].addTool(TupleToolTrackIsolation, name = "TrackIsoInfo")
        particles[0].addTool(TupleToolConeIsolation, name = "ConeIsoInfo")

        particles[0].ToolList += ["TupleToolTrackIsolation/TrackIsoInfo","TupleToolConeIsolation/ConeIsoInfo"]
        particles[0].TrackIsoInfo.MaxConeAngle = 0.5
        particles[0].TrackIsoInfo.Verbose = True
        particles[0].ConeIsoInfo.MinConeSize = 0.5 # ONLY USE ANGLE OF 0.5
        particles[0].ConeIsoInfo.MaxConeSize = 0.5 # ONLY USE ANGLE OF 0.5
        particles[0].ConeIsoInfo.Verbose = True

    # Set correct name depending on ee or mumu
    if 'ee' in lepton_mode:
        loki_name = 'JPsEE'
    else:
        loki_name = 'JPsMM'
    LoKi_Tool = getLoKiTool(loki_name, location_list[0],is_mdst)
    particles[0].ToolList += ["LoKi::Hybrid::TupleTool/LoKi_Tool{}".format(loki_name)]
    particles[0].addTool(LoKi_Tool)

    if is_mc:
        particles[0].ToolList += [
            'TupleToolMCBackgroundInfo'
        ]

        # Add MC tuple tools
        mctruth = dtt.addTupleTool('TupleToolMCTruth')
        dtt.ToolList += ['TupleToolMCTruth']
        dtt.TupleToolMCTruth.ToolList += [
            'MCTupleToolKinematic',
            'MCTupleToolHierarchy',
            'MCTupleToolPID',
            'MCTupleToolReconstructed'
        ]
        particles[0].addTupleTool('TupleToolMCTruth')
        particles[0].ToolList += ['TupleToolMCTruth']

    DaVinci().UserAlgorithms += [dtt]
   # tuple_seq = SelectionSequence('{}_SelSeq'.format(tuple_name), tuple_selection)

    return True #tuple_seq.sequence()


def tuple_sequence():
    """Return the sequencer used for running tuple algorithms.

    The sequencer is configured such that all members are run, as their filter
    flags are ignored.
    """
    seq = GaudiSequencer('TupleSeq')
    seq.IgnoreFilterPassed = True

    return seq
