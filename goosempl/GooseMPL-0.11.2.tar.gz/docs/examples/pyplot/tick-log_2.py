import matplotlib
import matplotlib.pyplot as plt

plt.style.use(["goose", "goose-latex"])

fig, ax = plt.subplots()

ax.set_xscale("log")
ax.set_yscale("log")

ax.set_xlim([2e-2, 2e-1])
ax.set_ylim([2e1, 2e3])

ax.plot([0.02, 0.1, 0.2], [20, 1000, 2000])

ax.xaxis.set_major_locator(
    matplotlib.ticker.LogLocator(
        subs=(
            1,
            2,
        )
    )
)
ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

plt.savefig("tick-log_2.svg")
plt.close()
