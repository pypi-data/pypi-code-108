from Configurables import DaVinci, GaudiSequencer

from helpers import tuple_maker

name = 'Bs2JpsiPhi'
line = 'BetaSBs2JpsiPhiDetachedLine'
is_mc = DaVinci().Simulation
tuple_seq = tuple_maker.tuple_maker(
    name,
    decay='B_s0 -> ^(J/psi(1S) -> ^mu+ ^mu-) ^(phi(1020) -> ^K+ ^K-)',
    branches={
        'B'       : 'B_s0 ->  (J/psi(1S) ->  mu+  mu-)  (phi(1020) ->  K+  K-)',
        'Jpsi'    : 'B_s0 -> ^(J/psi(1S) ->  mu+  mu-)  (phi(1020) ->  K+  K-)',
        'muplus'  : 'B_s0 ->  (J/psi(1S) -> ^mu+  mu-)  (phi(1020) ->  K+  K-)',
        'muminus' : 'B_s0 ->  (J/psi(1S) ->  mu+ ^mu-)  (phi(1020) ->  K+  K-)',
        'X'       : 'B_s0 ->  (J/psi(1S) ->  mu+  mu-) ^(phi(1020) ->  K+  K-)',
        'hplus'   : 'B_s0 ->  (J/psi(1S) ->  mu+  mu-)  (phi(1020) -> ^K+  K-)',
        'hminus'  : 'B_s0 ->  (J/psi(1S) ->  mu+  mu-)  (phi(1020) ->  K+ ^K-)'
    },
    stripping_line=line,
    is_mc=is_mc,
    input_type=DaVinci().InputType
)
dtt = tuple_seq.Members[-1]

# Alternate mass hypotheses
fitter_configs = [
    # B -> KplusPiMuMu
    ('B2KpPiJpsi', {'Beauty -> Meson (phi(1020) -> ^K+ X-)': 'pi+'}),
    # B -> KminusPiMuMu
    ('B2KmPiJpsi', {'Beauty -> Meson (phi(1020) -> X+ ^K-)': 'pi-'}),
    # Lb -> pKMuMu (Kplus)
    ('pKMuMuKplus', {'Beauty -> Meson (phi(1020) -> ^K+ X-)': 'p+'}),
    # Lb -> pKMuMu (Kminus)
    ('pKMuMuKminus', {'Beauty -> Meson (phi(1020) -> X+ ^K-)': 'p~-'})
]
for fitter_name, substitutions in fitter_configs:
    fitter = dtt.B.addTupleTool('TupleToolDecayTreeFitter/{}'.format(fitter_name))
    fitter.Verbose = True
    fitter.Substitutions = substitutions
    fitter.daughtersToConstrain = ['J/psi(1S)']
    fitter.constrainToOriginVertex = True

docas = dtt.B.addTupleTool('TupleToolDOCA')
doca_name, location1, location2 = zip(
    *[[
          'hplus_hminus',
          'B_s0 ->  (J/psi(1S) ->   mu+   mu-)  (phi(1020) ->  ^K+   K-)',
          'B_s0 ->  (J/psi(1S) ->   mu+   mu-)  (phi(1020) ->   K+  ^K-)'
      ],
      [
          'muplus_muminus',
          'B_s0 ->  (J/psi(1S) ->  ^mu+   mu-)  (phi(1020) ->   K+   K-)',
          'B_s0 ->  (J/psi(1S) ->   mu+  ^mu-)  (phi(1020) ->   K+   K-)'
      ],
      [
          'hplus_muplus',
          'B_s0 ->  (J/psi(1S) ->   mu+   mu-)  (phi(1020) ->  ^K+   K-)',
          'B_s0 ->  (J/psi(1S) ->  ^mu+   mu-)  (phi(1020) ->   K+   K-)'
      ],
      [
          'hplus_muminus',
          'B_s0 ->  (J/psi(1S) ->   mu+   mu-)  (phi(1020) ->  ^K+   K-)',
          'B_s0 ->  (J/psi(1S) ->   mu+  ^mu-)  (phi(1020) ->   K+   K-)'
      ],
      [
          'hminus_muplus',
          'B_s0 ->  (J/psi(1S) ->   mu+   mu-)  (phi(1020) ->   K+  ^K-)',
          'B_s0 ->  (J/psi(1S) ->  ^mu+   mu-)  (phi(1020) ->   K+   K-)'
      ],
      [
          'hminus_muminus',
          'B_s0 ->  (J/psi(1S) ->   mu+   mu-)  (phi(1020) ->   K+  ^K-)',
          'B_s0 ->  (J/psi(1S) ->   mu+  ^mu-)  (phi(1020) ->   K+   K-)'
      ]])
docas.Name = list(doca_name)
docas.Location1 = list(location1)
docas.Location2 = list(location2)

mc_tuples = []
if is_mc:
    mc_tuples.append(tuple_maker.mc_tuple_maker(
        name,
        '[[B_s0]cc ==> ^(J/psi(1S) ==> ^mu+ ^mu-) ^(phi(1020) ==> ^K+ ^K-)]CC',
        {
            'B'       : '[[B_s0]cc ==>  (J/psi(1S) ==>  mu+  mu-)  (phi(1020) ==>  K+  K-)]CC',
            'Jpsi'    : '[[B_s0]cc ==> ^(J/psi(1S) ==>  mu+  mu-)  (phi(1020) ==>  K+  K-)]CC',
            'muplus'  : '[[B_s0]cc ==>  (J/psi(1S) ==> ^mu+  mu-)  (phi(1020) ==>  K+  K-)]CC',
            'muminus' : '[[B_s0]cc ==>  (J/psi(1S) ==>  mu+ ^mu-)  (phi(1020) ==>  K+  K-)]CC',
            'X'       : '[[B_s0]cc ==>  (J/psi(1S) ==>  mu+  mu-) ^(phi(1020) ==>  K+  K-)]CC',
            'hplus'   : '[[B_s0]cc ==>  (J/psi(1S) ==>  mu+  mu-)  (phi(1020) ==> ^K+  K-)]CC',
            'hminus'  : '[[B_s0]cc ==>  (J/psi(1S) ==>  mu+  mu-)  (phi(1020) ==>  K+ ^K-)]CC'
        }
    ))

seq = tuple_maker.tuple_sequence()
seq.Members += [tuple_seq] + mc_tuples
