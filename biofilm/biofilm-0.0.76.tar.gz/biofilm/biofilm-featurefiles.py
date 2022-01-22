import matplotlib
matplotlib.use('module://matplotlib-sixel')
import dirtyopts
import numpy as np
from lmz import *
import matplotlib.pyplot as plt
import collections

doc = '''

heeh? i probably check which features have been chosen most often?

--infiles str+ ''
'''

args = dirtyopts.parse(doc)
paramlists = []
for e in args.infiles:
    d = np.load(e,allow_pickle=True)
    m = d[f'arr_2']
    paramlists.append(m)




# count all the things
dd = collections.defaultdict(int)

for li in paramlists:
    for z in li:
        dd[z]+= 1

import pprint
pprint.pprint(dd)

scores= []
for li in paramlists:
    score =  sum([dd[e] for e in li])/ len(li)
    scores.append(score)

i = np.argmax(scores)
pprint.pprint([(e,dd[e]) for e in paramlists[i].tolist()])
