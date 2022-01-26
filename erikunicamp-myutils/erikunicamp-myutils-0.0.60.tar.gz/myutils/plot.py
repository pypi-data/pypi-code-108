import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.collections as mc
import numpy as np
from myutils.geo import get_shp_points

palettes = {
        'saturated': ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999'],
        'pastel': ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999'],
        }

##########################################################
def export_subplots(ax, fig, labels, outdir, pad=0.3, prefix='', fmt='pdf'):
    n = ax.shape[0]*ax.shape[1]
    for k in range(n):
        i = k // ax.shape[1]
        j = k  % ax.shape[1]
        ax[i, j].set_title('')

    for k in range(n):
        i = k // ax.shape[1]
        j = k  % ax.shape[1]
        coordsys = fig.dpi_scale_trans.inverted()
        extent = ax[i, j].get_window_extent().transformed(coordsys)
        x0, y0, x1, y1 = extent.extents

        if isinstance(pad, list):
            x0 -= pad[0]; y0 -= pad[1]; x1 += pad[2]; y1 += pad[3];
        else:
            x0 -= pad; y0 -= pad; x1 += pad; y1 += pad;

        bbox =  matplotlib.transforms.Bbox.from_extents(x0, y0, x1, y1)
        fig.savefig(os.path.join(outdir, prefix + labels[k] + '.' + fmt),
                      bbox_inches=bbox)

##########################################################
def hex2rgb(hexcolours, normalize=False, alpha=None):
    n = len(hexcolours)
    rgbcolours = np.zeros((n, 3), dtype=float)

    for i, h in enumerate(hexcolours):
        rgbcolours[i, :] = np.array([int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)])

    if alpha != None:
        rgbcolours = np.concatenate([rgbcolours, np.ones((n, 1))*alpha], axis=1)

    if normalize:
        rgbcolours[:, :3] = rgbcolours[:, :3] / 255

    return rgbcolours

##########################################################
def create_meshgrid(x, y, nx=100, ny=100, relmargin=.1):
    """Create a meshgrid considering @x and @y bounds with @nx, @ny tiles
    and relative margins @relmargins"""

    marginx = (max(x) - min(x)) * relmargin
    marginy = (max(y) - min(y)) * relmargin
    xrange = [np.min(x) - marginx, np.max(x) + marginx]
    yrange = [np.min(y) - marginy - .15, np.max(y) + marginy]
    dx = (xrange[1] - xrange[0]) / nx
    dy = (yrange[1] - yrange[0]) / ny
    xx, yy = np.mgrid[xrange[0]:xrange[1]:(nx*1j), yrange[0]:yrange[1]:(ny*1j)]
    return xx, yy, dx, dy

#############################################################
def plot_graph_coords(vcoords, ecoords, ax, shppath):
    """Plot the grpah, with vertices colored by accessibility."""

    if not ax: fig, ax = plt.subplots(figsize=(7, 7))

    sc = ax.scatter(vcoords[:, 0], vcoords[:, 1], c='k',
            linewidths=0, alpha=.8, s=3, zorder=10) # vertices

    segs = mc.LineCollection(ecoords, colors='k', linewidths=.5, alpha=.5) # edges
    ax.add_collection(segs)

    if shppath: # border
        mapx, mapy = get_shp_points(shppath)
        ax.plot(mapx, mapy, c='dimgray')

    return ax

##########################################################
def plot_graph(gin, plotpath='/tmp/mygraph.png', inverty=False, ax=None, shppath=''):
    """Plot the graph @gin which can be an igraph object or a graphml file path. If @shppath is provided, plot the border given by @shppath."""

    import igraph
    if type(gin) == str: g = igraph.Graph.Read(gin)
    else: g = gin

    for attrs in [('lon', 'lat'), ('posx', 'posy'), ('x', 'y')]:
        if attrs[0] in g.vertex_attributes():
            xattr = attrs[0]; yattr = attrs[1]

    if inverty: ax.invert_yaxis()

    vcoords = np.array([(x, y) for x, y in zip(g.vs[xattr], g.vs[yattr])])
    vcoords = vcoords.astype(float)

    ecoords = []
    for e in g.es:
        ecoords.append([ [float(g.vs[e.source][xattr]), float(g.vs[e.source][yattr])],
                [float(g.vs[e.target][xattr]), float(g.vs[e.target][yattr])], ])

    ax = plot_graph_coords(vcoords, ecoords, ax, shppath)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(plotpath)
