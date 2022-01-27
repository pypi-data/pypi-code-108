import matplotlib.pyplot as plt
import numpy as np

import GooseMPL as gplt

plt.style.use(["goose", "goose-latex", "goose-autolayout"])


fig, ax = plt.subplots()

ax.set_xscale("log")
ax.set_yscale("log")

ax.set_xlim([1e0, 1e4])
ax.set_ylim([1e-2, 1e4])

x = np.logspace(1, 3, 10)
y = 0.001 * x ** 2.0
yerr = 0.1 * np.random.random(x.shape) * x
sign = np.random.random(x.shape)
sign = sign / np.abs(sign)
y = y + 0.1 * sign * yerr

ax.errorbar(x, y, yerr=yerr, marker="o")

gplt.fit_powerlaw(x, y, yerr=yerr, axis=ax, c="r", extrapolate=dict(ls="--", c="r"), auto_fmt="x")

ax.legend()

plt.savefig("fit_powerlaw_yerr.svg")
plt.close()
