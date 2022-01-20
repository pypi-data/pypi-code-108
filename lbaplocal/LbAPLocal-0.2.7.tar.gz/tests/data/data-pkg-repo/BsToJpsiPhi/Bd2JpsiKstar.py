from Configurables import DaVinci, GaudiSequencer

from helpers import tuple_maker

name = 'Bd2JpsiKstar'
line = 'BetaSBd2JpsiKstarDetachedLine'
is_mc = DaVinci().Simulation
tuple_seq = tuple_maker.tuple_maker(
    name,
    decay='[B0 ->  ^(J/psi(1S) ->  ^mu+  ^mu-)  ^(K*(892)0 ->  ^K+  ^pi-)]CC',
    branches={
        'B'       : '[B0 ->  (J/psi(1S) ->  mu+  mu-)  (K*(892)0 ->  K+  pi-)]CC',
        'Jpsi'    : '[B0 -> ^(J/psi(1S) ->  mu+  mu-)  (K*(892)0 ->  K+  pi-)]CC',
        'muplus'  : '[B0 ->  (J/psi(1S) -> ^mu+  mu-)  (K*(892)0 ->  K+  pi-)]CC',
        'muminus' : '[B0 ->  (J/psi(1S) ->  mu+ ^mu-)  (K*(892)0 ->  K+  pi-)]CC',
        'X'       : '[B0 ->  (J/psi(1S) ->  mu+  mu-) ^(K*(892)0 ->  K+  pi-)]CC',
        'hplus'   : '[B0 ->  (J/psi(1S) ->  mu+  mu-)  (K*(892)0 -> ^K+  pi-)]CC',
        'hminus'  : '[B0 ->  (J/psi(1S) ->  mu+  mu-)  (K*(892)0 ->  K+ ^pi-)]CC'
    },
    stripping_line=line,
    is_mc=is_mc,
    input_type=DaVinci().InputType
)
dtt = tuple_seq.Members[-1]

# Alternate mass hypotheses
fitter_configs = [
    # B -> KplusPiMuMu
    ('Jpsipipi', {
        'Beauty -> Meson (K*(892)0  -> ^K+ X-)': 'pi+',
        'Beauty -> Meson (K*(892)~0 -> ^K- X+)': 'pi-'
    }),
    # B -> KminusPiMuMu
    ('JpsiKK', {
        'Beauty -> Meson (K*(892)0  -> X+ ^pi-)': 'K-',
        'Beauty -> Meson (K*(892)~0 -> X- ^pi+)': 'K+'
    }),
    # Lb -> pKMuMu (Kplus)
    ('Jpsippi', {
        'Beauty -> Meson (K*(892)0  -> ^K+ X-)': 'p+',
        'Beauty -> Meson (K*(892)~0 -> ^K- X+)': 'p~-'
    }),
    # Lb -> pKMuMu (Piminus)
    ('JpsipK', {
        'Beauty -> Meson (K*(892)0  -> X+ ^pi-)': 'p~-',
        'Beauty -> Meson (K*(892)~0 -> X- ^pi+)': 'p+'
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
          'hplus_hminus',
          '[B0 ->  (J/psi(1S) ->   mu+   mu-)  (K*(892)0 ->  ^K+   pi-)]CC',
          '[B0 ->  (J/psi(1S) ->   mu+   mu-)  (K*(892)0 ->   K+  ^pi-)]CC'
      ],
      [
          'muplus_muminus',
          '[B0 ->  (J/psi(1S) ->  ^mu+   mu-)  (K*(892)0 ->   K+   pi-)]CC',
          '[B0 ->  (J/psi(1S) ->   mu+  ^mu-)  (K*(892)0 ->   K+   pi-)]CC'
      ],
      [
          'hplus_muplus',
          '[B0 ->  (J/psi(1S) ->   mu+   mu-)  (K*(892)0 ->  ^K+   pi-)]CC',
          '[B0 ->  (J/psi(1S) ->  ^mu+   mu-)  (K*(892)0 ->   K+   pi-)]CC'
      ],
      [
          'hplus_muminus',
          '[B0 ->  (J/psi(1S) ->   mu+   mu-)  (K*(892)0 ->  ^K+   pi-)]CC',
          '[B0 ->  (J/psi(1S) ->   mu+  ^mu-)  (K*(892)0 ->   K+   pi-)]CC'
      ],
      [
          'hminus_muplus',
          '[B0 ->  (J/psi(1S) ->   mu+   mu-)  (K*(892)0 ->   K+  ^pi-)]CC',
          '[B0 ->  (J/psi(1S) ->  ^mu+   mu-)  (K*(892)0 ->   K+   pi-)]CC'
      ],
      [
          'hminus_muminus',
          '[B0 ->  (J/psi(1S) ->   mu+   mu-)  (K*(892)0 ->   K+  ^pi-)]CC',
          '[B0 ->  (J/psi(1S) ->   mu+  ^mu-)  (K*(892)0 ->   K+   pi-)]CC'
      ]])
docas.Name = list(doca_name)
docas.Location1 = list(location1)
docas.Location2 = list(location2)

mc_tuples = []
if is_mc:
    mc_tuples.append(tuple_maker.mc_tuple_maker(
        name,
        '[[B0]cc ==> ^(J/psi(1S) ==> ^mu+ ^mu-) ^([K*(892)0]cc ==> ^K+ ^pi-)]CC',
        {
            'B'       : '[[B0]cc ==>  (J/psi(1S) ==>  mu+  mu-)  ([K*(892)0]cc ==>  K+  pi-)]CC',
            'Jpsi'    : '[[B0]cc ==> ^(J/psi(1S) ==>  mu+  mu-)  ([K*(892)0]cc ==>  K+  pi-)]CC',
            'muplus'  : '[[B0]cc ==>  (J/psi(1S) ==> ^mu+  mu-)  ([K*(892)0]cc ==>  K+  pi-)]CC',
            'muminus' : '[[B0]cc ==>  (J/psi(1S) ==>  mu+ ^mu-)  ([K*(892)0]cc ==>  K+  pi-)]CC',
            'X'       : '[[B0]cc ==>  (J/psi(1S) ==>  mu+  mu-) ^([K*(892)0]cc ==>  K+  pi-)]CC',
            'hplus'   : '[[B0]cc ==>  (J/psi(1S) ==>  mu+  mu-)  ([K*(892)0]cc ==> ^K+  pi-)]CC',
            'hminus'  : '[[B0]cc ==>  (J/psi(1S) ==>  mu+  mu-)  ([K*(892)0]cc ==>  K+ ^pi-)]CC'
        }
    ))

seq = tuple_maker.tuple_sequence()
seq.Members += [tuple_seq] + mc_tuples
