# -*-Python-*-
# Created by izzov at 24 Feb 2021  05:48

"""
This GUI is used to make tweaks to the current axes after the figure is created
in order to spruce it up for presenting or publishing
"""

OMFITx.Label('All changes apply to the current axes')

# global


def add_grid(location):
    grid(scratch['grid'])


def set_aspect(location):
    axis(scratch['aspect'])


def entitle(location):
    ax = gca()
    scratch.setdefault('tfs', 14)
    ax.set_title(scratch['title'], fontsize=scratch['tfs'])


with OMFITx.same_row():
    ax = gca()
    if ax.get_title():
        scratch['title'] = ax.get_title()
    OMFITx.Entry("scratch['title']", lbl='title', default="Plasma Current", postcommand=entitle)
    OMFITx.Entry("scratch['tfs']", lbl='font size', default=14, postcommand=entitle)

with OMFITx.same_row():
    OMFITx.ComboBox("scratch['grid']", {'on': 'on', 'off': False}, lbl='grid', default='off', postcommand=add_grid)
    OMFITx.ComboBox(
        "scratch['aspect']", {'equal': 'equal', 'image': 'image', 'auto': 'auto'}, lbl='aspect', default='auto', postcommand=set_aspect
    )


# x-axis


def set_xlim(location):
    ax = gca()
    ax.set_xlim(scratch['xlim'])


def set_xscale(location):
    ax = gca()
    ax.set_xscale(scratch['xscale'])


def set_xticks(location):
    ax = gca()
    ax.set_xticks(scratch['xticks'])


def set_xticklabels(location):
    ax = gca()
    scratch.setdefault('xfs', 12)
    ax.set_xticklabels(scratch['xtick_labels'], fontsize=scratch['xfs'])


def set_xlabel(location):
    ax = gca()
    scratch.setdefault('xfs', 12)
    ax.set_xlabel(scratch['xlabel'], fontsize=scratch['xfs'])


OMFITx.Tab('x-axis')

with OMFITx.same_row():
    ax = gca()
    if ax.get_xlabel():
        scratch['xlabel'] = ax.get_xlabel()
    OMFITx.Entry("scratch['xlabel']", lbl='xlabel', default="$\mathregular{t-t_{0}}$ $[{\mu}s]$", postcommand=set_xlabel)
    OMFITx.Entry("scratch['xfs']", lbl='font size', default=12, postcommand=set_xlabel)

with OMFITx.same_row():
    ax = gca()
    scratch['xlim'] = ax.get_xlim()
    OMFITx.Entry("scratch['xlim']", lbl='xlim', default=[0, 1], postcommand=set_xlim)
    OMFITx.ComboBox("scratch['xscale']", {'linear': 'linear', 'log': 'log'}, lbl='xscale', default='linear', postcommand=set_xscale)
with OMFITx.same_row():
    ax = gca()
    if any(ax.get_xticks()):
        scratch['xticks'] = ax.get_xticks()
    if any(ax.get_xticklabels()):
        scratch['xtick_labels'] = ax.get_xticklabels()
    elif any(ax.get_xticks()):
        scratch['xtick_labels'] = ax.get_xticks()
    OMFITx.Entry("scratch['xticks']", lbl='xticks', default=linspace(0, 1, 5), postcommand=set_xticks)
    OMFITx.Entry("scratch['xtick_labels']", lbl='xtick labels', default=linspace(0, 1, 5), postcommand=set_xticklabels)

# y-axis


def set_ylim(location):
    ax = gca()
    ax.set_ylim(scratch['ylim'])


def set_yscale(location):
    ax = gca()
    ax.set_yscale(scratch['yscale'])


def set_yticks(location):
    ax = gca()
    ax.set_yticks(scratch['yticks'])


def set_yticklabels(location):
    ax = gca()
    scratch.setdefault('yfs', 12)
    ax.set_yticklabels(scratch['ytick_labels'], fontsize=scratch['yfs'])


def set_ylabel(location):
    ax = gca()
    scratch.setdefault('yfs', 12)
    ax.set_ylabel(scratch['ylabel'], fontsize=scratch['yfs'])


OMFITx.Tab('y-axis')

with OMFITx.same_row():
    ax = gca()
    if ax.get_ylabel():
        scratch['ylabel'] = ax.get_ylabel()
    OMFITx.Entry("scratch['ylabel']", lbl='ylabel', default="$\mathregular{I_{p}}$ [MA]", postcommand=set_ylabel)
    OMFITx.Entry("scratch['yfs']", lbl='font size', default=12, postcommand=set_ylabel)

with OMFITx.same_row():
    ax = gca()
    scratch['ylim'] = ax.get_ylim()
    OMFITx.Entry("scratch['ylim']", lbl='ylim', default=[0, 1], postcommand=set_ylim)
    OMFITx.ComboBox("scratch['yscale']", {'linear': 'linear', 'log': 'log'}, lbl='yscale', default='linear', postcommand=set_yscale)
with OMFITx.same_row():
    ax = gca()
    if any(ax.get_yticks()):
        scratch['yticks'] = ax.get_yticks()
    if any(ax.get_yticklabels()):
        scratch['ytick_labels'] = ax.get_yticklabels()
    elif any(ax.get_yticks()):
        scratch['ytick_labels'] = ax.get_yticks()
    OMFITx.Entry("scratch['yticks']", lbl='yticks', default=linspace(0, 1, 5), postcommand=set_yticks)
    OMFITx.Entry("scratch['ytick_labels']", lbl='ytick labels', default=linspace(0, 1, 5), postcommand=set_yticklabels)


# add vertical and horizontal lines


def add_vertical_lines(location):
    ax = gca()
    yl = ax.get_ylim()
    scratch['vls'] = []
    scratch.setdefault('lstyle', '--')
    scratch.setdefault('lcolor', 'k')
    for xvl in scratch['xvls']:
        scratch['vls'].append(ax.plot([xvl, xvl], yl, linestyle=scratch['lstyle'], color=scratch['lcolor']))


def remove_vertical_lines():
    ax = gca()
    if scratch['vls']:
        for vl in scratch['vls']:
            line = vl.pop(0)
            line.remove()


OMFITx.Tab('Add vertical lines')

with OMFITx.same_row():
    OMFITx.Entry("scratch['lcolor']", lbl='color', default='k')
    OMFITx.Entry("scratch['lstyle']", lbl='style', default='--')
with OMFITx.same_row():
    OMFITx.Entry("scratch['xvls']", lbl='add at x', default=[0.5, 1.0], postcommand=add_vertical_lines)
    OMFITx.Button('remove all', remove_vertical_lines)


def add_horizontal_lines(location):
    ax = gca()
    xl = ax.get_xlim()
    scratch['hls'] = []
    scratch.setdefault('lstyle', '--')
    scratch.setdefault('lcolor', 'k')
    for yhl in scratch['yhls']:
        scratch['hls'].append(ax.plot(xl, [yhl, yhl], linestyle=scratch['lstyle'], color=scratch['lcolor']))


def remove_horizontal_lines():
    ax = gca()
    if scratch['hls']:
        for hl in scratch['hls']:
            line = hl.pop(0)
            line.remove()


OMFITx.Tab('Add horizontal lines')

with OMFITx.same_row():
    OMFITx.Entry("scratch['lcolor']", lbl='color', default='k')
    OMFITx.Entry("scratch['lstyle']", lbl='style', default='--')
with OMFITx.same_row():
    OMFITx.Entry("scratch['yhls']", lbl='add at y', default=[0.5, 1.0], postcommand=add_horizontal_lines)
    OMFITx.Button('remove all', remove_horizontal_lines)
