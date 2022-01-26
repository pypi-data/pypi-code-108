import matplotlib.pyplot as plt
import numpy as np

import GooseMPL as gplt

plt.style.use(["goose", "goose-latex", "goose-autolayout"])


fig, ax = plt.subplots()

x = np.linspace(0, 1, 20)
y = 12.3 + 45.6 * x
yerr = 1.0 * np.ones(y.shape)
yerr[10] = y[10] * 0.5
y[10] = y[10] * 0.75

ax.errorbar(x, y, yerr=yerr, marker="o")

offset, slope, details = gplt.fit_linear(
    x, y, yerr=yerr, axis=ax, c="r", extrapolate=dict(ls="--", c="r")
)

plt.savefig("fit_linear.svg")
plt.close()
