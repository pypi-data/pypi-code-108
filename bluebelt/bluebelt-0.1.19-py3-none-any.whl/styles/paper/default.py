import bluebelt.styles.defaults as defaults


# pattern plot | pyplot.plot
line = {
    'marker': None,
    'linewidth': 1,
    'color': defaults.blue+(1,),
    'linestyle': 'solid',
}

dotted_line = {
    'marker': None,
    'linewidth': 1,
    'color': defaults.blue,
    'linestyle': 'dotted',
    'linewidth': 1,
}

dashed_line = {
    'marker': None,
    'linewidth': 1,
    'color': defaults.blue,
    'linestyle': 'dashed',
    'linewidth': 1,
}
scatter = {
    'linewidth': 0,
    'marker': 'o',
    'markersize': 7,
    'markerfacecolor': defaults.blue,
    'markeredgewidth': 0,
    'markeredgecolor': defaults.blue,
    'alpha': 0.7,
}

observations = {
    'linewidth': 0,
    'marker': 'o',
    'markersize': 5,
    'markerfacecolor': defaults.black,
    'markeredgewidth': 0,
    'markeredgecolor': defaults.black,
    'alpha': 1,
}

out_of_bounds = {
    'linewidth': 0,
    'marker': 'o',
    'markersize': 5,
    'markerfacecolor': defaults.blue,
    'markeredgewidth': 0,
    'markeredgecolor': defaults.blue,
    'alpha': 1,
}

outliers = {
    'linewidth': 0,
    'marker': '+',
    'markersize': 7,
    'markerfacecolor': defaults.red,
    'markeredgewidth': 1,
    'markeredgecolor': defaults.red,
    'alpha': 1,
}

area = {
    'color': None,
    'hatch': '////',
    'linestyle': 'dashed',
    'linewidth': 0.5,
}

fill_between = {
    'color': None,
    'hatch': '////',
    'edgecolor': defaults.blue+(1,),
    'linestyle': '-',
    'linewidth': 0,
}

hist = {
    'density': True, 
    'alpha': 1,
    'edgecolor': None,
    'facecolor': defaults.blue,
    'fill': False,
    'hatch': '//',
    'linestyle': 'solid',
    'linewidth': 1,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}