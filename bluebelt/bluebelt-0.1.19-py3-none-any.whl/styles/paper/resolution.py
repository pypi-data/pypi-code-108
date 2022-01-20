import bluebelt.styles.defaults as defaults

# main plot | pyplot.plot
plot = {
    'marker': None,
    'zorder': 20,
    'linestyle': '-',
    'linewidth': 1,
    'color': defaults.black,
}

# main plot | pyplot.axhline
axhline = {
    'marker': None,
    'zorder': 20,
    'linestyle': '--',
    'linewidth': 1,
    'color': defaults.blue,
}


optimum_fill_between = {
    'color': None,
    'edgecolor': defaults.blue,
    'facecolor': None,
    'hatch': '\\\\\\',
    'linestyle': 'dashed',
    'linewidth': 0.5,
}

# text | pyplot.text
text = {
    'backgroundcolor': defaults.white,
    'color': defaults.blue,
    'va': 'center',
    'ha': 'left',
    'size': defaults.small,
    'zorder': 99,
}

# bounds_text | pyplot.text
bounds_text = {
    'backgroundcolor': defaults.white,
    'color': defaults.blue,
    'va': 'top',
    'ha': 'left',
    'size': defaults.small,
    'zorder': 99,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
    'size': defaults.medium
}
