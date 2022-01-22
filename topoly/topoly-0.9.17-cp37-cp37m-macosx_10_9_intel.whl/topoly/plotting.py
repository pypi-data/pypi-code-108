# plotting the matrix from the data given
# !/usr/bin/env python
# Copyright Michal Jamroz, 2014, jamroz@chem.uw.edu.pl

from matplotlib import gridspec, cm, patches
import matplotlib as mpl
mpl.use('Agg')
from .params import TopolyException, PlotFormat, Colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import Divider, Size, mpl_axes

plt.rcParams['svg.image_inline'] = True
plt.rcParams['font.size'] = 8
import math


class KnotMap:
    def __init__(self, protlen, protstart=0, patches=1, missing_residues=[], broken_chain=[], rasterized=False,
                 arrows=True, gridsize_cutoff=100):
        if patches == 0:
            raise TopolyException('No patches to plot!')
        self.protlen = protlen
        self.rast = rasterized
        self.protend = protlen
        self.protstart = protstart
        self.gridsize_cutoff = gridsize_cutoff
        self.fig = plt.figure(figsize=(5, 5))

        h = [Size.Fixed(0.64), Size.Fixed(3.12)]
        v = [Size.Fixed(1.2), Size.Fixed(3.12)]

        divider = Divider(self.fig, (0.0, 0.0, 1., 1.), h, v, aspect=False)
        self.minoraxe = mpl_axes.Axes(self.fig, divider.get_position())
        self.minoraxe.set_axes_locator(divider.new_locator(nx=1, ny=1))

        self.fig.add_axes(self.minoraxe)

        self.axes = []
        self.minoraxe.grid(True, linewidth=0.1)
        self.minoraxe.set_ylim(protstart - float(protlen)/200, protlen + float(protlen)/200)
        self.minoraxe.set_xlabel('Residue index', fontsize=11)
        # self.minoraxe.set_axis_bgcolor('#f0f0d6')
        # TODO new API in Matplotlib!!!
        self.minoraxe.set_facecolor('#f0f0d6')
        self.minoraxe.set_ylabel('Residue index', fontsize=11)
        self.minoraxe.set_xlim(protstart - float(protlen)/200, protlen + float(protlen)/200)
        self.arrows = arrows
        self.gids = []
        self.knot_ranges_for_gid = {}
        self.slipknot_ranges_for_gid = []

        tn = int((self.protend - self.protstart) / 5)
        if tn==0: tn=1

        ticks = [i for i in range(self.protstart, self.protend, tn)]

        min_dist_protend = int((self.protend - self.protstart) / 14)
        if ticks[-1] + min_dist_protend < self.protend:
            ticks.append(self.protend)
        else:
            ticks[-1] = self.protend

        mL = mpl.ticker.FixedLocator(
            list(ticks))  # [self.protstart]+[i for i in range(self.protstart,self.protend,50)]+[self.protend])
        self.minoraxe.xaxis.set_major_locator(mL)
        self.minoraxe.yaxis.set_major_locator(mL)

        if len(missing_residues) > 0:  # add spans for missing residues
            colorr = '#336666'
            alf = 0.05
            for r in missing_residues:
                d = r.split("-")
                if len(d) == 2:
                    self.minoraxe.axhspan(float(d[0]), float(d[1]), facecolor=colorr, alpha=alf, edgecolor='none')
                    self.minoraxe.axvspan(float(d[0]), float(d[1]), facecolor=colorr, alpha=alf, edgecolor='none')
                elif len(d) == 1:
                    self.minoraxe.axhline(y=float(d[0]), color=colorr, alpha=alf, linewidth=1)
                    self.minoraxe.axvline(x=float(d[0]), color=colorr, alpha=alf, linewidth=1)
        if len(broken_chain) > 0:  # add spans for missing residues
            colorr = 'red'
            alf = 0.2
            for r in broken_chain:
                self.minoraxe.axhline(y=float(r), color=colorr, alpha=alf, linewidth=0.5, linestyle='-')
                self.minoraxe.axvline(x=float(r), color=colorr, alpha=alf, linewidth=0.5, linestyle='-')
        self.knot_gids = []
        self.minoraxe.invert_yaxis()
        self.minoraxe.plot([protstart, protlen], [protstart, protlen], 'k:', lw=0.1, gid='diagonal')
        self.patches_counter = 0
        self.legend_gs = gridspec.GridSpec(nrows=patches, ncols=1, left=0.85, right=0.90, bottom=0.19, top=0.9,
                                           wspace=0.2)

        for i in range(patches):
            ax = self.fig.add_subplot(self.legend_gs[i, 0])
            self.axes.append(ax)

    def _addarrow(self, label, xy, xytext, gid, gidl):
        if self.arrows:
            if label == "knot core":
                ms = 25  # wieksza strzalka
                fc = "#428bca"
            elif label == "slipknot loop":
                ms = 15
                fc = "#fbb450"
            elif label == "slipknot tail":
                ms = 15
                fc = "#62c462"
            else:
                ms = 15
                fc = "gray"
            self.minoraxe.annotate(label, xy=xy, size='medium', xycoords='data', xytext=xytext, \
                                   arrowprops=dict(arrowstyle="fancy", color='none', fc=fc, alpha=0.8,
                                                   mutation_scale=ms, \
                                                   connectionstyle="angle3,angleA=0,angleB=-90", gid=gid), gid=gidl)

    def add_patch(self, WRdata, palette=Colors.Knots):
        x, y, z = WRdata["coordinates"]
        knot_name = WRdata["knot_name"]
        sk_type = WRdata["knot_type"]
        knot_range = WRdata["knot_range"]
        knot_tails = WRdata["knot_tails"]
        sknotloop = WRdata["sknot_loop"]
        sknottails = WRdata["sknot_tails"]

        gid = palette['name'] + "_" + knot_name.replace('_', '')
        self.knot_gids.append(gid)
        gid = gid + "_annotate"
        self.gids.append(gid)
        label_name = palette['name'] + " " + knot_name
        clim = [math.floor(min(min(z), 0)), math.ceil(max(z))]

        ticks = [clim[0], clim[0]+(clim[1]-clim[0])/2, clim[1]]

        if clim[0] < 0:
            colormap = cm.get_cmap(palette.get(knot_name, 'binary'), 21)
        else:
            colormap = cm.get_cmap(palette.get(knot_name, 'binary'), 10)

        if self.protlen > self.gridsize_cutoff:
            gridsize = self.protlen
        else:
            gridsize = self.gridsize_cutoff

        t = self.minoraxe.hexbin(x, y, C=z, cmap=colormap, rasterized=self.rast, alpha=1, gridsize=gridsize)
        t.set_clim(clim)
        cbar = self.fig.colorbar(t, cax=self.axes[self.patches_counter], ticks=ticks)  # ,cmap=cm.spring)
        self.patches_counter += 1
        cbar.set_label(label_name)

        if self.arrows:
            # add annotations
            x1 = min(x)
            x2 = max(x)
            y1 = min(y)
            y2 = max(y)

            knot_1, knot_N = knot_range

            scale = int(self.protend - self.protstart) / 20

            px = self.protstart + 6 * scale
            py = self.protstart + 2 * scale

            # unique v/h-lines
            htuples = []
            vtuples = []
            labtuple = []
            labtuple2 = []

            for i in range(len(knot_tails)):
                v = knot_tails[i]
                self.minoraxe.plot(v, v, lw=1.0, color='gray', linestyle='-', gid=gid + "_diag_KT_1" + str(i),
                                   marker='o', ms=0)
                mid = v[0] + (v[1] - v[0]) / 2
                self._addarrow("knot tail", (mid, mid - 15), (px + 2 * scale, py + 1 * scale), gid + "_ll2",
                               gid + "_l2")

            for i in range(len(sknotloop)):
                v = sknotloop[i]
                mid = v[0] + (v[1] - v[0]) / 2
                self._addarrow("slipknot loop", (mid, mid - 15), (px + 4 * scale, py + 2 * scale), gid + "_ll3",
                               gid + "_l3")
                # if i==0: # skip if the same are for knot vlines (show onlu for first sliploop
                #    vtuples.append( (v[0],v[0],self.protend,gid) )
                labtuple.append((v[1], gid))
                labtuple.append((v[0], gid))
                self.minoraxe.plot(v, v, lw=1.0, color='#fbb450', linestyle='-', gid=gid + "_diag_SL_1" + str(i),
                                   marker='o', ms=0)
            for i in range(len(sknottails)):
                v = sknottails[i]
                mid = v[0] + (v[1] - v[0]) / 2
                self._addarrow("slipknot tail", (mid, mid - 15), (px + 4 * scale, py + 5 * scale), gid + "_ll4",
                               gid + "_l4")
                labtuple.append((v[1], gid))
                labtuple.append((v[0], gid))
                self.minoraxe.plot(v, v, lw=1.0, color='#62c462', linestyle='-', gid=gid + "_diag_ST_1" + str(i),
                                   marker='o', ms=0)
                # htuples.append( (v[0],0,v[0],gid) )

            # labels, lines, resnumbers for knot area
            v = knot_range
            mid = v[0] + (v[1] - v[0]) / 2
            vtuples.append((v[0], v[0], self.protend, gid))
            htuples.append((v[1], 0, v[1], gid))
            labtuple2.append((v[1], gid))
            labtuple2.append((v[0], gid))
            # add arrow for knot area
            self._addarrow("knot core", (mid, mid - 15), (px + 6 * scale, py), gid + "_ll1", gid + "_l1")

            for h in set(htuples):
                self.minoraxe.hlines(h[0], h[1], h[2], lw=0.1, color='black', linestyles='-', gid=h[3] + "_hkr2")

            for h in set(vtuples):
                self.minoraxe.vlines(h[0], h[1], h[2], lw=0.1, color='black', linestyles='-', gid=h[3] + "_hkr2")

            tmp = []
            for h in set(labtuple2):
                if h[0] not in tmp and h[0] + 1 not in tmp and h[0] - 1 not in tmp:  # skip if labels would be too close
                    self.minoraxe.text(h[0] + 4, h[0], h[0], fontsize='small', gid=h[1] + '_textK1')
                    tmp.append(h[0])
            for h in set(labtuple):
                if h[0] not in tmp and h[0] + 1 not in tmp and h[0] - 1 not in tmp:
                    self.minoraxe.text(h[0] + 4, h[0], h[0], fontsize='small', gid=h[1] + '_textK1')
                    tmp.append(h[0])

            self.minoraxe.plot([knot_1, knot_N], [knot_1, knot_N], lw=2.8, color='#428bca', \
                               linestyle='-', gid=gid + "_diag1", marker='o', ms=5)  # knot core

    def close(self):
        plt.close(self.fig)

    def saveFile(self, filename, plot_format=PlotFormat.PNG):
        self.fig.savefig(filename + '.' + plot_format, format=plot_format, transparent=True)


class Reader:
    def __init__(self, input_data, cutoff=0.48, min_one_dim=2, min_spot=4, knot=''):
        self.data = {}
        self.cutoff = cutoff
        self.unknot = False

        if type(input_data) is dict:
            indices = self.read_dictionary_input(input_data)
        elif type(input_data) is str and '>' in input_data:
            indices = self.read_knotprot_input(input_data)
        elif type(input_data) is list:
            indices = self.read_list_input(input_data, knot)
        else:
            indices = self.read_stringdictionary_input(input_data)

        self.seq_start = min(indices)
        self.seq_end = max(indices)

        self.clean_data(min_one_dim, min_spot)

        if not self.data:
            self.unknot = True
            return

        self.overall_type = self.decide_type()
        return

    def read_knotprot_input(self, data):
        lines = data.split('\n')
        indices = []
        column = 0

        for line in lines:
            if len(line) < 2 or 'HEAD' in line or 'UNKNOT' in line:
                continue
            elif line[0] == '#':
                indices = [int(line.split()[1]), int(line.split()[2])]
                d = line.strip().split()[3:-3]  # data - without first three and last three columns
                for i in range(3, len(d) - 2):
                    if float(d[i].replace(">", "")) / 100 < self.cutoff:
                        column = i
                        break
            else:
                d = line.strip().split()
                for i in range(2, column + 1):
                    for knot in d[i].split(','):
                        if knot == '0' or knot == '0_1':
                            continue
                        if knot not in self.data:
                            self.data[knot] = []
                        probability = 0.9 - (i - 2) * 0.03
                        self.data[knot].append((int(d[0]), int(d[1]), probability))
        return indices

    def read_list_input(self, data, knot):
        self.data[knot] = []
        for k in range(len(data)):
            line = data[k]
            for l in range(len(line)):
                value = float(line[l])
                if value != 0 and value > self.cutoff:
                    self.data[knot].append((k+1, l+1, value))
        return [1, len(data)]

    def read_stringdictionary_input(self, data):
        lines = data.split('\n')
        indices = []
        for line in lines:
            ident, value = line.strip().split(' ')
            ident = [int(x) for x in ident.split(',')]
            indices += ident
            values = value.strip('{}').split(';')
            for value in values:
                knot, prob = value.split(':')
                prob = float(prob)
                if knot == '0' or knot == '0_1' or prob < self.cutoff:
                    continue
                if knot not in self.data.keys():
                    self.data[knot] = []
                self.data[knot].append((ident[0], ident[1], prob))
        return indices

    def read_dictionary_input(self, data):
        indices = []
        for ident in data.keys():
            indices += [ident[0], ident[1]]
            if type(data[ident]) is dict:
                knots = list(zip(list(data[ident].keys()),list(data[ident].values())))
            else:
                knots = [(data[ident],1)]
            for knot, probability in knots:
                if knot == '0_1' or probability < self.cutoff:
                    continue
                if knot not in self.data.keys():
                    self.data[knot] = []
                self.data[knot].append((ident[0], ident[1], probability))
        return indices

    def clean_data(self, min_one_dim, min_spot):
        to_remove = []
        one_dim = {}
        for knot in self.data.keys():
            if len(self.data[knot]) < min_spot:
                to_remove.append(knot)
            else:
                one_dim['x'] = [x for x, y, z in self.data[knot]]
                one_dim['y'] = [y for x, y, z in self.data[knot]]
                if any(len(one_dim[_]) < min_one_dim for _ in one_dim.keys()):
                    to_remove.append(knot)
        for k in list(set(to_remove)):
            self.data.pop(k, None)
        return

    def decide_type(self):
        for knot in self.data.keys():
            for x, y, prob in self.data[knot]:
                if x == self.seq_start and y == self.seq_end:
                    return 'K'
        return 'S'

    def getUniqueKnots(self):
        return list(self.data.keys())

    def getKnot(self, knot_type):
        if knot_type not in self.data.keys():
            return None
        x_data = [x for x, y, z in self.data[knot_type]]
        y_data = [y for x, y, z in self.data[knot_type]]
        z_data = [z for x, y, z in self.data[knot_type]]

        maxX = max(x_data)
        maxY = max(y_data)
        minX = min(x_data)
        minY = min(y_data)

        slipknotloop = []
        slipknottails = []
        knottails = []

        if minX == self.seq_start and maxY == self.seq_end:
            sknot = "K"
            C_cut = self.seq_end - minY + 1
            N_cut = maxX
            knottails.append((self.seq_start, maxX))
            knottails.append((minY, self.seq_end))
        else:
            sknot = "S"
            if maxY == self.seq_end:
                C_cut = self.seq_end - minY
            else:
                C_cut = self.seq_end - maxY
            if minX == self.seq_start:
                N_cut = maxX
            else:
                N_cut = minX - 1

        if self.seq_start < minX:
            if maxX >= minX:
                slipknotloop.append((minX, maxX))
            slipknottails.append((self.seq_start, minX - 1))
            if self.seq_end == maxY:
                knottails.append((minY, self.seq_end))
        if self.seq_end > maxY:
            if maxY >= minY:
                slipknotloop.append((minY, maxY))
            slipknottails.append((maxY + 1, self.seq_end))
            if self.seq_start == minX:
                knottails.append((self.seq_start, maxX))

        out = {"coordinates": (x_data, y_data, z_data),
               "knot_name": knot_type,
               "knot_type": sknot,
               "knot_range": (maxX + 1, minY - 1),
               "knot_tails": knottails,
               "sknot_loop": slipknotloop,
               "sknot_tails": slipknottails,
               "knot_length": minY - 1 - (maxX + 1) + 1,
               "C_cut": C_cut,
               "N_cut": N_cut}
        return out



