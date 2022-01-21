# -*- coding: utf-8 -*-

import numpy as np
import hyperclip
# from matplotlib import pyplot as plt
from time import time

n = 7
m = 3

hyperplanes = [hyperclip.Hyperplane().set_by_points(np.random.random((n,n))) for i_m in range(m)]


st = time()
X = np.random.random((10**6,n))

id_pos_side = np.ones(X.shape[0])
for hyp in hyperplanes:
    id_pos_side = np.all((id_pos_side, hyp.side(X)), axis=0)

mc_time = time()-st


hc = hyperclip.Hyperclip(cython=True).set_hyperplanes(hyperplanes)
st = time()
vol = hc.volume()

hc_time = time() - st

print('MonteCarlo :', round(id_pos_side.mean(),6), 'time :', round(mc_time,6))
print('Hyperclip :', round(vol,6), 'time :', round(hc_time,6))

