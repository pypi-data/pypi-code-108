import matplotlib.pyplot as plt
import numpy as np

import GooseMPL as gplt

plt.style.use(["goose", "goose-latex", "goose-autolayout"])


fig, ax = plt.subplots()

ax.set_xscale("log")
ax.set_yscale("log")

ax.set_xlim([1e0, 1e4])
ax.set_ylim([1e-2, 1e4])

x = np.logspace(1, 3, 1000)
y = 0.001 * x ** 2.0
y = y + 0.1 * np.random.random(x.shape) - 0.05

ax.plot(x, y)

gplt.fit_powerlaw(x, y, axis=ax, c="r", extrapolate=dict(ls="--", c="r"))

plt.savefig("fit_powerlaw.svg")
plt.close()
