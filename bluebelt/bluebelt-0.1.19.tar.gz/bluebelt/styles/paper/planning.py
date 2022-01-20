import bluebelt.styles.defaults as defaults

# main plot | pyplot.plot
plot_quantity = {
    'color': defaults.black,
    'linestyle': 'solid',
    'linewidth': 1,
    'zorder': 90,
}
# main plot | pyplot.fill_between
fill_between_quantity = {
    'color': None,
    'hatch': '////',
    'linestyle': 'dashed',
    'linewidth': 0.5,
    'zorder': 50,
}


# main plot | pyplot.plot
plot_distribution = {
    'color': defaults.blue,
    'linestyle': 'solid',
    'linewidth': 1,
    'zorder': 90,
}
# main plot | pyplot.fill_between
fill_between_distribution = {
    'color': None,
    'edgecolor': defaults.blue,
    'hatch': '\\\\\\\\',
    'linestyle': 'dashed',
    'linewidth': 0.5,
    'zorder': 50,
}

plot_quality = {
    'color': defaults.green,
    'linestyle': 'solid',
    'linewidth': 1,
    'zorder': 90,
}
# main plot | pyplot.fill_between
fill_between_quality = {
    'color': None,
    'edgecolor': defaults.green,
    'hatch': '||||',
    'linestyle': 'dashed',
    'linewidth': 0.5,
    'zorder': 50,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}