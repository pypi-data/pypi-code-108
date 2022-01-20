from Configurables import DaVinci, GaudiSequencer

from helpers import tuple_maker

name = 'Bu2JpsiKplus'
line = 'BetaSBu2JpsiKDetachedLine'
is_mc = DaVinci().Simulation
tuple_seq = tuple_maker.tuple_maker(
    name,
    decay='[B+ -> ^(J/psi(1S) -> ^mu+ ^mu-) ^K+]CC',
    branches={
        'B'       : '[B+ ->  (J/psi(1S) ->  mu+  mu-)  K+]CC',
        'Jpsi'    : '[B+ -> ^(J/psi(1S) ->  mu+  mu-)  K+]CC',
        'muplus'  : '[B+ ->  (J/psi(1S) -> ^mu+  mu-)  K+]CC',
        'muminus' : '[B+ ->  (J/psi(1S) ->  mu+ ^mu-)  K+]CC',
        'hplus'   : '[B+ ->  (J/psi(1S) ->  mu+  mu-) ^K+]CC'
    },
    stripping_line=line,
    is_mc=is_mc,
    input_type=DaVinci().InputType
)
dtt = tuple_seq.Members[-1]

# Alternate mass hypotheses
fitter_configs = [
    # B -> KplusPiMuMu
    ('B2PiJpsi', {
        'Beauty -> Meson ^K+': 'pi+',
        'Beauty -> Meson ^K-': 'pi-'
    }),
    # Lb -> pKMuMu (Kplus)
    ('B2pJpsi', {
        'Beauty -> Meson ^K+': 'p+',
        'Beauty -> Meson ^K-': 'p~-'
    })
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
          'muplus_muminus',
          '[B+ ->  (J/psi(1S) ->  ^mu+   mu-)   K+]CC',
          '[B+ ->  (J/psi(1S) ->   mu+  ^mu-)   K+]CC'
      ],
      [
          'hplus_muplus',
          '[B+ ->  (J/psi(1S) ->   mu+   mu-)  ^K+]CC',
          '[B+ ->  (J/psi(1S) ->  ^mu+   mu-)   K+]CC'
      ],
      [
          'hplus_muminus',
          '[B+ ->  (J/psi(1S) ->   mu+   mu-)  ^K+]CC',
          '[B+ ->  (J/psi(1S) ->   mu+  ^mu-)   K+]CC'
      ]])
docas.Name = list(doca_name)
docas.Location1 = list(location1)
docas.Location2 = list(location2)

mc_tuples = []
if is_mc:
    mc_tuples.append(tuple_maker.mc_tuple_maker(
        name,
        '[[B+]cc ==> ^K+ ^(J/psi(1S) ==> ^mu+ ^mu-)]CC',
        {
            'B'       : '[[B+]cc ==>  K+  (J/psi(1S) ==>  mu+  mu-)]CC',
            'Jpsi'    : '[[B+]cc ==>  K+ ^(J/psi(1S) ==>  mu+  mu-)]CC',
            'muplus'  : '[[B+]cc ==>  K+  (J/psi(1S) ==> ^mu+  mu-)]CC',
            'muminus' : '[[B+]cc ==>  K+  (J/psi(1S) ==>  mu+ ^mu-)]CC',
            'hplus'   : '[[B+]cc ==> ^K+  (J/psi(1S) ==>  mu+  mu-)]CC'
        }
    ))

seq = tuple_maker.tuple_sequence()
seq.Members += [tuple_seq] + mc_tuples
