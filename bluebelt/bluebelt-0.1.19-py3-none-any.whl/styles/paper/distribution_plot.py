import bluebelt.styles.defaults as defaults

# main plot | pyplot.plot
scatter = {
    'linewidth': 0,
    'marker': 'o',
    'zorder': 50,
    'color': defaults.black+(1,),
}

plot = {
    'marker': None,
    'color': defaults.red,
    'linewidth': 1,
    'linestyle': 'solid',
    'zorder': 30, 
}

# stat text | pyplot.text
stat_text = {
    'ha': 'right',
    'va': 'bottom',
    'zorder': 90,
}

# array text | pyplot.text
array_text = {
    'ha': 'left',
    'va': 'top',
    'zorder': 90,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
    'size': defaults.small
}

# plot title | fig.suptitle
suptitle = {
    'ha': 'left',
    'size': defaults.medium
}
