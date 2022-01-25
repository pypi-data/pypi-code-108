import sys
sys.path.append('.')

# This code is needed is pyxml if installed
pyxml=None
index = 0
for p in sys.path:
    if -1 != p.find('pyxml'):
         pyxml = p
    index += 1
if None != pyxml:
    sys.path.remove(pyxml)


import datetime
INTEGER_TYPE = type(0)
FLOAT_TYPE = type(0.0)
STRING_TYPE = type("")
DATETIME_TYPE = type(datetime.datetime.strptime('1970-01-01T00:00:00',
                                                '%Y-%m-%dT%H:%M:%S' ))
LIST_TYPE = type([])
SLICE_TYPE = type(slice(0))

# Create unique object for selecting all tags
ALL_TAGS = type("ALL_TAGS", (), {})()

import xml.etree.ElementTree as ET

def _append_value(parent,
                value):
    valueElement = ET.Element('value')
    if DATETIME_TYPE == type(value):
        valueElement.text = str(value.isoformat() + 'Z')
        valueElement.set('type', 'java.util.Date')
    else:
        valueElement.text = str(value)
        if FLOAT_TYPE == type(value):
            valueElement.set('type', 'java.lang.Float')
        elif INTEGER_TYPE == type(value):
            valueElement.set('type', 'java.lang.Integer')
        else:
            valueElement.set('type', 'java.lang.String')
    parent.append(valueElement)


def _append_item(parent,
               name,
               value):
    nameElement = ET.Element('name')
    nameElement.text = name
    parent.append(nameElement)
    _append_value(parent, value)


def _append_tag(parent,
              tag,
              values):
    tagElement = ET.Element('or')
    for value in values:
        if SLICE_TYPE == type(value):
            sliceElement = ET.Element('and')
            begin = ET.Element('gte')
            _append_item(begin, tag, value.start)
            sliceElement.append(begin)
            end = ET.Element('lt')
            _append_item(end, tag, value.stop)
            sliceElement.append(end)
            tagElement.append(sliceElement)
        else:
            equals = ET.Element('eq')
            _append_item(equals, tag, value)
            tagElement.append(equals)
    if 1 == len(tagElement):
        for child in tagElement:
            parent.append(child)
        return
    parent.append(tagElement)


def _create_attachment(selections):
    attachment = ET.Element('and')
    for tag in selections.keys():
        _append_tag(attachment, tag, selections[ tag ])
    if 1 == len(attachment):
        for child in attachment:
            return child
        return
    return attachment


def __fix_value_url(el):
    """ Change a file based `url` tag into simply a path for easy opening by client """
    el_type = el.get('type')
    el_text = el.text
    if el_type == 'java.net.URI' and el_text.startswith('file:'):
        el_text = el_text[5:]
        if el_text.startswith('///'):
            el_text = el_text[2:]
    return el_text


def _get_values(el):
    """ Return the text for a single or a list of them """

    val = el.find('value')
    if val is not None:
        return __fix_value_url(val)

    # We've got a list of values
    ret = []
    vals = el.findall('values/value')
    for val in vals:
        ret.append(__fix_value_url(val))

    return ret


def resolve_selection(catalog, attachment, element = None, triggers = None):
    conjunction = ''
    tags = ''
    if type('') == type(element):
        elementToUse = [element]
    else:
        elementToUse = element
    if ALL_TAGS is elementToUse:
       tags = tags + conjunction + 'alltags=true'
       conjunction = "&"
    else:
      if None != elementToUse:
        for ele in elementToUse:
            tags = tags + conjunction + 'tag=' + ele
            conjunction = "&"
      if None != triggers and len(triggers) != 0:
        for trigger in triggers:
            tags = tags + conjunction + 'tag=' + trigger
            conjunction = '&'
    query = '?ordering=begin_time&' + tags    
    entries = catalog.get_selection(attachment, query)
    entrySeq = entries.findall('entry')
    results = []
    for entry in entrySeq:
        result = []
        if  ALL_TAGS is element:
            for xmlElement in entry.findall('tags/tag'):
                result.append((xmlElement.find('name').text, _get_values(xmlElement)))
        else:
            for ele in elementToUse:
                xmlElement = entry.find('tags/tag/[name="' + ele + '"]')
                if None != xmlElement:
                    val_or_vals = _get_values(xmlElement)
                    result.append(val_or_vals)
        results.append(result)
    
    # if requested only one element, return a flat list
    if not ALL_TAGS is elementToUse and 1 == len(elementToUse):
        results = [item for sublist in results for item in sublist]
    
    return results


class Selections(object):
    """
    This class captures on or more selections to be sent to the Catalog.
    """

    def __init__(self, catalog, tag, value, element = None, triggers = None ):
        if None == tag and None == value:
            # Assume this is a copy operation (rename catalog for clarity)
            rhs = catalog
            self.catalog = rhs.catalog
            self.element = rhs.element
            self.selections = rhs.selections.copy()
            self.triggers = rhs.triggers
            return
        self.catalog = catalog
        self.element = element
        self.selections = {}
        self.select(tag, value)
        self.triggers = triggers


    def typeToUse(self, value):
        if None == value:
            return value
        if SLICE_TYPE == type(value):
            return slice(self.typeToUse(value.start),
                         self.typeToUse(value.stop),
                         self.typeToUse(value.step))
        if LIST_TYPE == type(value):
            result = []
            for v in value:
                result.append(self.typeToUse(v))
            return result
        if STRING_TYPE != type(value):
            return value
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S" )
        except ValueError:
            pass
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M" )
        except ValueError:
            pass
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H" )
        except ValueError:
            pass
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d" )
        except ValueError:
            pass
        return value


    def __add__(self, rhs):
        result = Selections(self, None, None)
        result += rhs
        return result


    def __iadd__(self, rhs):
        for tag in rhs.selections:
            if tag in self.selections:
                self.selections[ tag ].extend(rhs.selections[ tag ])
        for tag in rhs.selections:
            if not tag in self.selections:
                self.selections[ tag ] = rhs.selections[ tag ]
        return self


    def __getitem__(self, key):
        self.resolve()
        return self.resolution[key]


    def __len__(self):
        self.resolve()
        return len(self.resolution)


    def __repr__(self):
        try:
            self.resolve()
        except TypeError as e:
            if 'Response is "text/html", not "text/xml"' == e.message:
                raise IOError('Failed to get correct reponse from Web Service')
        return str(self.resolution)


    def __str__(self):
        return str(self.selections)


    def select(self, tag, value):
        valueToUse = self.typeToUse(value)
        if tag in self.selections:
            existing = self.selections[ tag ]
        else:
            existing = self.selections[ tag ] = []
        if LIST_TYPE == type(valueToUse):
            self.selections[ tag ].extend(valueToUse)
        else:
            self.selections[ tag ].append(valueToUse)
        self.resolution = None
        return self


    def resolve(self):
        if hasattr(self, 'resolution') and None != self.resolution:
            return self.resolution
        attachment = _create_attachment(self.selections)
        self.resolution = resolve_selection(self.catalog, attachment,
                                            self.element, self.triggers)
