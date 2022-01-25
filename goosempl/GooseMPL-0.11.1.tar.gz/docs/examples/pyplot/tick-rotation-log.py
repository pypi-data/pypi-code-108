import matplotlib
import matplotlib.pyplot as plt

plt.style.use(["goose", "goose-latex"])

fig, ax = plt.subplots()

ax.set_xscale("log")
ax.set_yscale("log")

ax.set_xlim([2e-2, 2e-1])
ax.set_ylim([2e1, 2e3])

ax.plot([0.01, 0.1, 1.0], [20, 200, 2000])

ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.get_xaxis().set_minor_formatter(matplotlib.ticker.ScalarFormatter())

plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
plt.setp(ax.xaxis.get_minorticklabels(), rotation=45)

plt.savefig("tick-rotation-log.svg")
plt.close()
