from __future__ import division, unicode_literals
import os
import io
import sys
import copy
import logging
import traceback

import numpy as np
try:
    import yaml
except ImportError:
    pass
import xml.etree.ElementTree as ET


logger = logging.getLogger('TEMPLATE')

##########

TEMPLATE = {
    'window-title': '',
    'color-mode': 'dark',
    'time-window': None,
    'plots': [],
    'font-size': 10,
}

PLOT = {
    'channels': {},
    'row': 0,
    'col': 0,
    'colspan': 1,
    'yrange': 'auto',
}

CURVE = {
    'color': None,
    'width': 1,
    'unit': None,
    'scale': 1,
    'offset': 0,
}

DEFAULT_PEN_COLORS = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    '#7f7f7f',
    '#bcbd22',
    '#17becf',
]
COLOR_INDEX = 0


def random_color():
    c = [int(i) for i in list(np.random.rand(3)*255)]
    return '#{:02x}{:02x}{:02x}'.format(*c)


def get_color_by_index(i):
    try:
        return DEFAULT_PEN_COLORS[i]
    except IndexError:
        return random_color()


def get_pen_color():
    global COLOR_INDEX
    try:
        c = DEFAULT_PEN_COLORS[COLOR_INDEX]
    except IndexError:
        return random_color()
    COLOR_INDEX += 1
    return c

##########
# create new bare template/plot/curve, populated with defaults


def _new_template(**kwargs):
    t = copy.copy(TEMPLATE)
    t.update(**kwargs)
    return t


def _new_plot(**kwargs):
    t = copy.copy(PLOT)
    t.update(**kwargs)
    return t


def _new_curve(**kwargs):
    t = copy.copy(CURVE)
    t.update(**kwargs)
    if not t['color']:
        t['color'] = get_pen_color()
    return t

##########
# create specified layout from list of {channel: curve} dicts


def convert_layout(template, targ):
    """convert table layout to grid/stack/single"""
    channels = []
    for plot in template['plots']:
        for chan in plot['channels']:
            channels.append(chan)
    if targ == 'grid':
        layout = _convert_grid(channels)
    elif targ == 'stack':
        layout = _convert_stack(channels)
    elif targ == 'single':
        layout = _convert_single(channels)
    else:
        raise ValueError("unknown layout: {}".format(targ))
    template['plots'] = layout


def _convert_grid(channels):
    num = len(channels)
    rows = int(np.ceil(np.sqrt(num)))
    cols = int(np.ceil(float(num)/rows))
    layout = []
    r = 0
    c = 0
    for i, chan in enumerate(channels):
        layout.append(
            _new_plot(
                channels=[chan],
                row=r,
                col=c,
            ))
        c += 1
        if c == cols:
            c = 0
            r += 1
    return layout


def _convert_stack(channels):
    layout = []
    for i, chan in enumerate(channels):
        layout.append(
            _new_plot(
                channels=[chan],
                row=i,
            )
        )
    return layout


def _convert_single(channels):
    layout = [
        _new_plot(
            channels=channels,
        )
    ]
    return layout

##########


class TemplateError(Exception):
    pass


def validate_template(template):
    try:
        time_window = template.get('time-window')
        if time_window:
            try:
                template['time-window'] = [float(t) for t in template['time-window']]
            except TypeError:
                template['time-window'] = float(template['time-window'])
        for plot in template['plots']:
            channels = plot['channels']
            if isinstance(channels, dict):
                plot['channels'] = [{chan: curve} for chan, curve in channels.items()]
            else:
                plot['channels'] = [dict(chan.items()) for chan in channels]
    except:
        raise TemplateError("error parsing template")


def load_template(path):
    """load template from path or stdin (if path == '-')

    Could be template file or channel table description.

    """
    if path == '-':
        ext = ''
        f = sys.stdin
    else:
        ext = os.path.splitext(path)[1]
        f = io.open(path, 'r', encoding='utf-8')
    data = io.StringIO(f.read())
    f.close()

    if ext == '':
        template = None
        ltype = None
        for func in [
                template_from_yaml,
                template_from_stp,
                template_from_txt,
                template_from_dvxml,
        ]:
            data.seek(0)
            try:
                logger.debug("template try: {}".format(func.__name__))
                template, ltype = func(data)
                break
            except:
                logger.debug(traceback.format_exc(0))
                continue
        if template is None:
            raise TemplateError("Could not parse template.")
    elif ext in ['.yaml', '.yml']:
        template, ltype = template_from_yaml(data)
    elif ext == '.stp':
        template, ltype = template_from_stp(data)
    elif ext == '.txt':
        template, ltype = template_from_txt(data)
    elif ext == '.xml':
        template, ltype = template_from_dvxml(path)
    else:
        raise TemplateError("Unknown template format '{}'".format(ext))

    validate_template(template)

    if 'window-title' not in template or not template['window-title']:
        template['window-title'] = os.path.basename(os.path.splitext(path)[0])

    return template, ltype

##########


def template_from_chans(chan_layout):
    """create template from channel table description

    """
    layout = []
    channels = []
    chans = []
    r = 0
    c = 0
    for chan in chan_layout + ['.']:
        if chan in [',', '.']:
            layout.append(
                _new_plot(
                    channels=chans,
                    row=r,
                    col=c,
                ))
            chans = []
            if chan == ',':
                c += 1
            elif chan == '.':
                c = 0
                r += 1
        else:
            chans.append({chan: _new_curve()})
            channels.append(chan)
    template = _new_template()
    template['window-title'] = ' '.join(channels)
    template['plots'] = layout
    logger.debug("created template from channel list")
    return template, 'table'


def template_from_yaml(data):
    """load template from YAML file data

    """
    try:
        t = yaml.safe_load(data)
    except NameError:
        raise TemplateError("YAML package not available.")
    template = _new_template()
    template.update(t)
    logger.debug("loaded YAML template")
    return template, 'table'


def template_from_stp(data):
    """create template from StripTool .stp file data

    """
    template = _new_template()

    curves = {}
    colors = []
    version = None
    for line in data:
        try:
            key, val = line.strip().split(None, 1)
        except ValueError:
            key = line.strip()
            val = None

        if key == 'Strip.Time.Timespan':
            template['time-window'] = [-float(val), 0]

        elif key == 'Strip.Color.Background':
            bgcolor = [int(v)/256 for v in val.split()]
            if bgcolor == [255, 255, 255]:
                template['black-on-white'] = True
            else:
                template['black-on-white'] = False

        elif 'Strip.Curve.' in key:
            curve, field = key.split('.')[2:4]
            curve = int(curve)
            if curve not in curves:
                curves[curve] = {}
            curves[curve][field] = val

        elif 'Strip.Color.Color' in key:
            color = [int(v)/256 for v in val.split()]
            colors.append(color)

        elif key == 'StripConfig':
            version = val

    if not version:
        raise TemplateError("could not determine StripConfig version")

    channels = []
    for k, v in sorted(curves.items()):
        if 'Name' not in v:
            continue
        channel = v['Name']
        color = colors[k]
        ymin = float(v['Min'])
        ymax = float(v['Max'])
        try:
            scale = 2.0 / (ymax - ymin)
        except ZeroDivisionError:
            scale = 1
        offset = abs((ymax + ymin) * scale / 2.0)
        channels.append({channel: _new_curve(
            color=color,
            scale=scale,
            offset=offset,
        )})

    template['plots'] = [
        _new_plot(
            channels=channels,
            yrange=[-1, 1],
        )
    ]

    logger.debug("loaded StripTool template")
    return template, 'single'


def template_from_txt(data):
    """create template from text file data

    One channel per line, with optional space separated y axis limits,
    e.g.:

    L1:GRD-ISC_LOCK_STATE_N
    L1:LSC-DARM_ERR_DQ -100 100

    """
    template = _new_template()

    channels = []
    yranges = []
    for i, line in enumerate(data):
        line = line.strip()
        if not line or line[0] == '#':
            continue

        tmp = line.split()
        channel = str(tmp[0])
        if len(tmp) == 1:
            yrange = 'auto'
        elif len(tmp) == 3:
            yrange = [float(tmp[1]), float(tmp[2])]
        else:
            logger.warning("could not parse line: {}".format(line))
            continue

        channels.append({channel: _new_curve()})
        yranges.append(yrange)

    if not channels:
        raise TemplateError("no channels loaded")

    layout = _convert_grid(channels)
    for plot, yrange in zip(layout, yranges):
        plot['yrange'] = yrange

    template['plots'] = layout
    logger.debug("loaded TXT template")
    return template, 'grid'


def template_from_dvxml(xmlFile):
    '''
    Create an NDScope template from a dataviewer template.
    Requires that the argument "xmlFile" be a valid dataviewer template.
    '''
    e = ET.parse(xmlFile)
    root = e.getroot()
    ch = []
    ymin = []
    ymax = []
    autorange = []
    for child in root:
        if child.tag == 'NAME':
            ch.append(child.text)
        elif child.tag == 'YMIN':
            ymin.append(child.text)
        elif child.tag == 'YMAX':
            ymax.append(child.text)
        elif child.tag == 'AUTO':
            autorange.append(child.text)
    template = _new_template()
    channels = []
    yranges = []
    for ii, jj, kk, ll in zip(ch, ymin, ymax, autorange):
        channels.append({ii: _new_curve()})
        if ll != 1:
            yranges.append([float(jj), float(kk)])
        else:
            yranges.append('auto')
    if not channels:
        raise TemplateError('No channels loaded')
    lay = _convert_grid(channels)
    for plot, yrange in zip(lay, yranges):
        plot['yrange'] = yrange
    template['plots'] = lay
    logger.debug("loaded Dataviewer XML template")
    return(template, 'grid')
