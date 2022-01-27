import matplotlib.pyplot as plt
import numpy as np
import scipy.special

import GooseMPL as gplt

plt.style.use(["goose", "goose-latex"])

# generate CDF

mu = 0.0
sigma = 1.0
x = np.sort(np.random.normal(mu, sigma, size=10000))
Px = np.linspace(0, 1, x.size)

# draw random number from CDF

y = gplt.random_from_cdf(shape=(10000), P=Px, x=x)

# plot result

prob_x, bin_x = gplt.histogram(x, bins=100, return_edges=False, density=True)
prob_y, bin_y = gplt.histogram(y, bins=100, return_edges=False, density=True)

xi = np.linspace(-5, 5, 10000)
Pi = 1.0 / (sigma * np.sqrt(2.0 * np.pi)) * np.exp(-0.5 * ((xi - mu) / sigma) ** 2.0)
Ci = 0.5 * (1.0 + scipy.special.erf((xi - mu) / (sigma * np.sqrt(2.0))))

fig, axes = gplt.subplots(ncols=2)

axes[0].plot(xi, Pi, color="k")
axes[0].plot(bin_x, prob_x, color="r")
axes[0].plot(bin_y, prob_y, color="g")
axes[0].set_xlabel(r"$x$")
axes[0].set_ylabel(r"$p$")

axes[1].plot(xi, Ci, color="k", label="analytical")
axes[1].plot(x, Px, color="r", label="discrete CDF")
axes[1].plot(np.sort(y), np.linspace(0, 1, y.size), color="g", label="drawn random numbers")
axes[1].set_xlabel(r"$x$")
axes[1].set_ylabel(r"$P$")
axes[1].legend()

plt.savefig("random_from_cdf.svg")
plt.close()
