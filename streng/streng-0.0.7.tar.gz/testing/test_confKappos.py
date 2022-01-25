import numpy as np
import matplotlib.pyplot as plt

from streng.ppp.materials.concrete import KapposConfined91

kc = KapposConfined91(fc=24.,
                      εco=0.002,
                      ρw=0.0047785,
                      bc=0.30,
                      s=0.20,
                      fyw=440.,
                      hoops_pattern=1)

εcs = np.linspace(0, 0.03, 101).tolist()
σcs = [kc.σc(εc) for εc in εcs]


fig, ax = plt.subplots()
line1, = ax.plot(εcs, σcs, '-', linewidth=2,
                 label='σ-ε')

ax.legend(loc='right')
ax.grid(True)
plt.show()
