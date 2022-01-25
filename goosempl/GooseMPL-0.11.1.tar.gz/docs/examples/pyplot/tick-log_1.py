import matplotlib
import matplotlib.pyplot as plt

plt.style.use(["goose", "goose-latex"])

fig, ax = plt.subplots()

ax.set_xscale("log")
ax.set_yscale("log")

ax.set_xlim([2e-2, 2e-1])
ax.set_ylim([2e1, 2e3])

ax.plot([0.02, 0.1, 0.2], [20, 1000, 2000])

ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.get_xaxis().set_minor_formatter(matplotlib.ticker.ScalarFormatter())

ax.set_xticks([])
ax.set_xticks([], minor=True)
ax.set_xticks([0.02, 0.1, 0.2])

plt.savefig("tick-log_1.svg")
plt.close()
