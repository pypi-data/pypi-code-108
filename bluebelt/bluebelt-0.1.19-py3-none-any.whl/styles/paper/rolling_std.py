import bluebelt.styles.defaults as defaults

# main plot | pyplot.plot
plot = {
    'color': defaults.black,
    'linestyle': 'solid',
    'linewidth': 1,
    'zorder': 90,
}
# main plot | pyplot.fill_between
fill_between = {
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