import bluebelt.styles.defaults as defaults


hist = {
    'density': True, 
    'alpha': 1, # alpha fraction 0-1
    'edgecolor': None, # color name, hex or None
    'facecolor': defaults.blue, # color name, hex or None
    'fill': False, #True, False
    'hatch': '//', # '/', '\', '|', '-', '+', 'x', 'o', 'O', '.' or '*'
    'linestyle': 'solid', # '-', '--', '-.', ':', '', (offset, on-off-seq), ...
    'linewidth': 1, # float
}

# plot used for normal distribution | pyplot.plot
normal_plot = {
    'color': defaults.blue,
    'linestyle': 'dashed',
    'linewidth': 1,
}