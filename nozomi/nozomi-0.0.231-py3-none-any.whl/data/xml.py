"""
Nozomi
XML Module
author: hugh@blinkybeach.com
"""
from typing import Dict, Any
from xml.etree import cElementTree as unsafeElementTree
from collections import defaultdict
from xml.dom import minidom

try:
    from defusedxml import cElementTree
except ImportError:
    cElementTree = None


class XML:

    wrapper_key = 'payload'

    @staticmethod
    def xmlstring_to_data(string: str) -> Any:

        if not cElementTree:
            raise NotImplementedError('Install defusedxml')

        element_tree = cElementTree.fromstring(string)
        output = XML._etree_to_dict(tree=element_tree)
        return output[XML.wrapper_key]

    @staticmethod
    def data_to_xmlstring(data: Any) -> str:

        data = {XML.wrapper_key: data}

        def _to_etree(d, root):
            if not d:
                pass
            elif isinstance(d, int):
                root.text = str(d)
            elif isinstance(d, str):
                root.text = d
            elif isinstance(d, dict):
                for k, v in d.items():
                    assert isinstance(k, str)
                    if k.startswith('#'):
                        assert k == '#text' and isinstance(v, str)
                        root.text = v
                    elif k.startswith('@'):
                        assert isinstance(v, str)
                        root.set(k[1:], v)
                    elif isinstance(v, list):
                        for e in v:
                            _to_etree(e, unsafeElementTree.SubElement(root, k))
                    else:
                        _to_etree(v, unsafeElementTree.SubElement(root, k))
            elif isinstance(d, list):
                for item in d:
                    _to_etree(
                        item,
                        unsafeElementTree.SubElement(root, XML.wrapper_key)
                    )
            else:
                raise TypeError('invalid type: ' + str(type(d)))

        assert isinstance(data, dict) and len(data) == 1
        tag, body = next(iter(data.items()))
        node = unsafeElementTree.Element(tag)

        _to_etree(body, node)

        return minidom.parseString(
            unsafeElementTree.tostring(node).decode('utf-8')
        ).toprettyxml(indent="    ")

    @staticmethod
    def _etree_to_dict(tree: cElementTree) -> Dict[str, Any]:

        if not cElementTree:
            raise NotImplementedError('Install defusedxml')

        t = tree

        tag = t.tag.split('}')[-1] if len(t.tag.split('}')) > 1 else t.tag
        d: Dict = {tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(XML._etree_to_dict, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if t.attrib:
            d[tag].update(('@' + k, v) for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[tag]['#text'] = text
            else:
                d[tag] = text

        for k in d.keys():
            v = d[k]
            if not isinstance(v, str):
                continue
            if v == 'True':
                d[k] = True
            if v == 'False':
                d[k] = False
            if v.isdigit():
                d[k] = int(v)
                continue
            if v.replace('.', '').isdigit():
                d[k] = float(v)
                continue
            continue

        return d
