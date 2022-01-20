import bluebelt.styles.defaults as defaults

# main plot | pyplot.plot
scatter = {
    'linewidth': 0,
    'marker': 'o',
    'zorder': 50,
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

# standard deviation text | pyplot.text
text = {
    'backgroundcolor': defaults.white+(0.3,),
    'va': 'top',
    'ha': 'left',
    'fontsize': defaults.xsmall
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}