import bluebelt.styles.defaults as defaults

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

# text | pyplot.text
text = {
    'backgroundcolor': defaults.white,
    'va': 'center',
    'ha': 'center',
    'zorder': 10,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
    'size': defaults.small
}

# plot title | pyplot.set_title
suptitle = {
    'ha': 'left',
    'size': defaults.medium
}
