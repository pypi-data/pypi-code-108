import bluebelt.styles.defaults as defaults

# main plot | pyplot.plot
observations = {
    'linewidth': 0,
    'marker': 'o',
    'zorder': 50,
}

# pattern plot | pyplot.plot
pattern = {
    'marker': None,
    'linewidth': 1,
    'zorder': 99,
    'color': defaults.blue+(1,),
    'linestyle': '-',
}

# out of bounds values | pyplot.plot
out_of_bounds = {
    'linewidth': 0,
    'marker': 'o',
    'markerfacecolor': defaults.blue+(1,),
    #'markeredgecolor': defaults.red+(1,),
    'zorder': 55,
}

# outlier background | pyplot.plot
outlier_background = {
    'linewidth': 0,
    'marker': 'o',
    'markersize': 17,
    'markerfacecolor': defaults.white,
    'zorder': 40, 
}

# outlier marker | pyplot.plot
outlier = {
    'linewidth': 0,
    'marker': 'o',
    'markersize': 9,
    'markerfacecolor': defaults.white,
    'markeredgecolor': defaults.black+(1,),
    'markeredgewidth': 1,
    'zorder': 45, 
}



# bandwidth fill_between | pyplot.fill_between
bandwidth_fill_between = {
    'color': None,
    'hatch': '////',
    'edgecolor': defaults.blue+(1,), # color name, hex or None
    'linestyle': '-',
    'linewidth': 0,
}

# lower plot | pyplot.plot
lower = {
    'marker': None,
    'linewidth': 1,
    'zorder': 99,
    'color': defaults.blue+(1,),
    'linestyle': '--',
}

# upper plot | pyplot.plot
upper = {
    'marker': None,
    'linewidth': 1,
    'zorder': 99,
    'color': defaults.blue+(1,),
    'linestyle': '--',
}

# histogram | pyplot.hist
histogram = {
    'density': True, 
    'alpha': 1, # alpha fraction 0-1
    'edgecolor': None, # color name, hex or None
    'facecolor': defaults.blue, # color name, hex or None
    'fill': False, #True, False
    'hatch': '//', # '/', '\', '|', '-', '+', 'x', 'o', 'O', '.' or '*'
    'linestyle': 'solid', # '-', '--', '-.', ':', '', (offset, on-off-seq), ...
    'linewidth': 1, # float
}

# stat text | pyplot.text
statistics = {
    'ha': 'left',
    'va': 'top',
    'zorder': 90,
    'size': defaults.xsmall,
}
# plot used for normal distribution | pyplot.plot
normal_plot = {
    'color': defaults.blue,
    'linestyle': 'dashed',
    'linewidth': 1,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}