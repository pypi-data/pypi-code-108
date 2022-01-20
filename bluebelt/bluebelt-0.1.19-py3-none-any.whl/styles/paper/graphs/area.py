import bluebelt.styles.defaults as defaults
from cycler import cycler

# main plot | pyplot.plot
plot = {
    #'color': defaults.black,
    'linestyle': 'solid',
    'linewidth': 3,
    'zorder': 90,
}

# main plot | pyplot.fill_between
stackplot = {
    'color': None,
    'hatch': '////',
    'linestyle': 'dashed',
    'linewidth': 0.5,
    'zorder': 50,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}