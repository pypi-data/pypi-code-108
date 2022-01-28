# SPDX-FileCopyrightText: 2019,2020 Freemelt AB
#
# SPDX-License-Identifier: Apache-2.0

# Built-in
from xml.dom import minidom

# PyPI
from svg.path import Line, CubicBezier
from svg.path import parse_path

# Project
from . import segment_handler


def read_svg(f):
    doc = minidom.parse(f)
    width, height = int(doc.getElementsByTagName('svg')[0].getAttribute('width')), int(doc.getElementsByTagName('svg')[0].getAttribute('height'))
    paths = get_paths(doc)
    doc.unlink()
    return paths, width, height

def get_rects(doc):
    rects = []
    for path in doc.getElementsByTagName('rect'):
        recdict = {}
        recdict['x'] = float(path.getAttribute('x'))
        recdict['y'] = float(path.getAttribute('y'))
        recdict['width'] = float(path.getAttribute('width'))
        recdict['height'] = float(path.getAttribute('height'))
        rects.append(recdict)
    return rects

def get_paths(doc):
    path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
    return path_strings

def handle_elements(element, width, height):
    l = []
    for el in element:
        for path_element in parse_path(el):
            if isinstance(path_element, Line):
                l.append(segment_handler.create_segment('Line', path_element, width, height))
            elif isinstance(path_element, CubicBezier):
                l.append((segment_handler.create_segment('Curve', path_element, width, height)))



    return l


def convert_svg(element, width, height):
    l = handle_elements(element, width, height)
    l1 =  [x for x in l if x != []]
    return l1