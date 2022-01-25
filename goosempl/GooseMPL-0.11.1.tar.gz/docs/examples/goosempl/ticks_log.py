import matplotlib.pyplot as plt
import numpy as np

import GooseMPL as gplt

plt.style.use(["goose", "goose-latex", "goose-autolayout"])


fig, ax = plt.subplots()

x = np.logspace(1, 3, 1000)
y = 0.001 * x ** 2.0

ax.plot(x, y)

ax.set_xscale("log")
ax.set_yscale("log")

ax.set_xlim([1e1, 1e3])
ax.set_ylim([0.06, 2000])

gplt.log_xticks(keep=[0, -1], axis=ax)
gplt.log_yticks(keep=[], axis=ax)
gplt.log_minoryticks(keep=[0, -1], axis=ax)

plt.savefig("ticks_log.svg")
plt.close()
