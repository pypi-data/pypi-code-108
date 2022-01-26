import json
from collections import OrderedDict
import xml.etree.ElementTree as ET
from string import Formatter

class TXMLElement(ET.Element):
    def __init__(self, tag, attrib={}, text=None, tail=None, **extra):
        super().__init__(tag, attrib, **extra)
        self.text = text
        self.tail = tail
        
    @classmethod
    def from_dict(cls, source):
        if not isinstance(source, dict):
            raise TypeError("source must be dict, not %s" % (
                source.__class__.__name__,))
        tag = source['tag']
        attrib =source['attrib']
        xml_element = cls(tag, attrib)
        xml_element.text = source['text']
        for sub_element in source:
            xml_element.append(cls.from_dict(sub_element))
        
        return xml_element
    
    @classmethod
    def from_element(cls, source):
        if not isinstance(source, ET.Element):
            raise TypeError("source must be ElementTree.Element, not %s" % (
                source.__class__.__name__,))
        xml_element = cls(source.tag, source.attrib)
        xml_element.text = source.text
        xml_element.tail = source.tail
        for sub_element in source:
            xml_element.append(cls.from_element(sub_element))
        return xml_element    
    
    @staticmethod
    def _to_dict(source):
        if not isinstance(source, ET.Element):
            raise TypeError("source must be ElementTree.Element, not %s" % (
                source.__class__.__name__,))        
        element = {}
        element['tag'] = source.tag
        element['attrib'] = source.attrib
        element['text'] = source.text
        element['children'] = [TXMLElement._to_dict(child) for child in source]
        return element
    
    @staticmethod
    def _to_diagram(source, indent=' '*4, show_attrib=False, level=0):
        if not isinstance(source, ET.Element):
            raise TypeError("source must be ElementTree.Element, not %s" % (
                source.__class__.__name__,)) 
        tail = ':' if show_attrib else ''
        string = '{}- {}{}\n'.format(indent*level, source.tag, tail)
        if show_attrib:
            for attrib in source.attrib:
                string += '{}- {}\n'.format(indent*(level+1), attrib)
        for child in source:
            string += TXMLElement._to_diagram(child, indent=indent, 
                                          show_attrib=show_attrib,
                                          level=level+1)
        return string
    
    
    def add_node(self, tag, attrib={}, text=None, tail=None, path=None, **extra):
        element = TXMLElement(tag, attrib, text, tail, **extra)
        self.append(element)
        return element    
    
    def to_diagram(self, indent=' '*4, show_attrib=False):
        return self._to_diagram(self, indent=indent, show_attrib=show_attrib)
        
    def to_dict(self):
        return self._to_dict(self)
    
    def __str__(self):
        return self.to_diagram(show_attrib=True)
    
    @staticmethod
    def _format_str(source, **args):
        if not isinstance(source, ET.Element):
            raise TypeError("source must be ElementTree.Element, not %s" % (
                source.__class__.__name__,)) 
        xml_str = TXMLElement._to_str(source)
        xml_formatted_str = xml_str.format(**args)
        return TXMLElement.from_str(xml_formatted_str)
    
    @staticmethod
    def _format_str_old_old(source, **args):
        if not isinstance(source, ET.Element):
            raise TypeError("source must be ElementTree.Element, not %s" % (
                source.__class__.__name__,)) 
        xml_str = json.dumps(TXMLElement._to_dict(source))
        xml_formatted_str = xml_str.format(**args)
        return TXMLElement.from_dict(xml_formatted_str)
    
    @staticmethod
    def _format_str_old(source, **args):
        if not isinstance(source, ET.Element):
            raise TypeError("source must be ElementTree.Element, not %s" % (
                source.__class__.__name__,)) 
        source.tag = source.tag.format(**args)
        if source.text:
            source.text = source.text.format(**args)
        if source.tail:
            source.tail = source.tail.format(**args)
        source.attrib = { key.format(**args): value.format(**args) for key,value in source.attrib.items()}
        for sub_element in source:
            TXMLElement._format_str(sub_element)
        
    def format_str(self, **args):
        return self._format_str(self, **args)
        
    @staticmethod
    def _iterate_append(root, source, argument_list={}):
        if not isinstance(root, ET.Element):
            raise TypeError('root node must be ElementTree.Element, not %s' % (
                root.__class__.__name__,))
        if not isinstance(source, ET.Element):
            raise TypeError('souce node must be ElementTree.Element, not %s' % (
                source.__class__.__name__,))
        element_str = ET.tostring(source, 'unicode')
        fieldnames = [fname for _, fname, _, _ in Formatter().parse(element_str) if fname]
        argnames = argument_list.keys()
        if set(fieldnames) != set(argnames):
            raise ValueError('mismatch between field names in source node and argument names in argument list')
        
        arg_size = set(map(len, argument_list.values()))
        if len(arg_size) > 1:
            raise ValueError('argument lists must have the same size')
        arg_size = arg_size[0]
        args_list = [dict(zip(argument_list,t)) for t in zip(*argument_list.values())]
        
        for args in args_list:
            element = ET.fromstring(element_str.format(**args))
            root.append(element)
        
    def iterate_append(self, source, argument_list, path=None):
        if path is None:
            root = self
        else:
            root = self.find(path)
        self._iterate_append(root, source=source, argument_list=argument_list)
        
    @staticmethod
    def _to_str(source, encoding='utf-8'):
        xml_str = ET.tostring(source)
        if not encoding:
            return xml_str
        else:
            return xml_str.decode(encoding)
    
    def to_str(self, encoding='utf-8'):
        return self._to_str(self, encoding=encoding)
    
    @classmethod
    def from_str(cls, source, encoding='utf-8'):
        if encoding:
            element = ET.fromstring(source.encode(encoding))
        else:
            element = ET.fromstring(source)
        return cls.from_element(element)
    

class TXMLTree(ET.ElementTree):
    def __init__(self, element=None, file=None,
                 version="1.0", encoding="UTF-8", doctype=None, system=None):
        super().__init__(element, file)
        if self._root is not None:
            self._root = TXMLElement.from_element(self._root)
        self._declarations = {
            'version': version,
            'encoding': encoding,
            'doctype': doctype,
            'system': system
        }
    
    def new_root(self, tag, attrib={}, text=None, tail=None, **extra):
        element = TXMLElement(tag, attrib, text, tail, **extra)
        self._root = element

    def add_node(self, tag, attrib={}, text=None, tail=None, path=None, **extra):
        if self._root is None:
            raise RuntimeError('root node is not initialized')
        element = TXMLElement(tag, attrib, text, tail, **extra)
        if path is None:
            root = self._root
        else:
            root = self._root.find(path)
        root.append(element)
        return element
        
        
    def set_root(self, element):
        if not isinstance(source, ET.Element):
            raise TypeError('root node must be ElementTree.Element, not %s' % (
                element.__class__.__name__,))
        if not isinstance(source, TXMLElement):
            self._root = TXMLElement.from_element(source)
        else:
            self._root = element
        
 
    @staticmethod
    def indent(elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                TXMLTree.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
                
    def write(self, file_or_filename,
              encoding=None,
              xml_declaration=None,
              default_namespace=None,
              *,
              short_empty_elements=True):
        """Write element tree to a file as XML.
        Arguments:
          *file_or_filename* -- file name or a file object opened for writing
          *encoding* -- the output encoding (default: US-ASCII)
          *xml_declaration* -- bool indicating if an XML declaration should be
                               added to the output. If None, an XML declaration
                               is added if encoding IS NOT either of:
                               US-ASCII, UTF-8, or Unicode
          *default_namespace* -- sets the default XML namespace (for "xmlns")
          *short_empty_elements* -- controls the formatting of elements
                                    that contain no content. If True (default)
                                    they are emitted as a single self-closed
                                    tag, otherwise they are emitted as a pair
                                    of start/end tags
        """
        if not encoding:
            encoding = "us-ascii"
        enc_lower = encoding.lower()
        with ET._get_writer(file_or_filename, enc_lower) as write:
            if (xml_declaration or
                    (xml_declaration is None and
                     enc_lower not in ("utf-8", "us-ascii", "unicode"))):
                declared_encoding = encoding
                if enc_lower == "unicode":
                    # Retrieve the default encoding for the xml declaration
                    import locale
                    declared_encoding = locale.getpreferredencoding()
                write("<?xml version='1.0' encoding='%s'?>\n" % (
                    declared_encoding,))
            else:
                qnames, namespaces = ET._namespaces(self._root, default_namespace)
                _serialize_xml(write, self._root, qnames, namespaces,
                          short_empty_elements=short_empty_elements)
                
    def save(self, filename, **kwargs):
        if not self._root:
            return None
        with open(filename, 'wb') as f:
            f.write('<?xml version="{version}" encoding="{encoding}" ?>\n'.format(**self._declarations).encode('utf8'))
            if (self._declarations.get('doctype', None)) and (self._declarations.get('system', None)):
                f.write('<!DOCTYPE {doctype} SYSTEM "{system}">\n'.format(**self._declarations).encode('utf8'))
            self.indent(self._root)
            self.write(f, 'utf-8', **kwargs)
            
    def to_dict(self):
        if self._root is None:
            return {}
        return self._root.to_dict()     
    
    def to_diagram(self, indent=' '*4, show_attrib=False):
        if self._root is None:
            return ''
        return self._root.to_diagram(indent=indent, show_attrib=show_attrib)
            
    def __str__(self):
        if self._root is None:
            return ''
        return self._root.to_diagram()    
    
    @staticmethod
    def _to_str(source, encoding='utf-8'):
        return TXMLElement._to_str(source._root, encoding=encoding)
    
    def to_str(self, encoding='utf-8'):
        return self._to_str(self, encoding=encoding)
    
    def format_str(self, **kwargs):
        cls = TXMLTree()
        cls._declarations = self._declarations
        cls._root = self._root.format_str(**kwargs)
        return cls
    
    
def _serialize_xml(write, elem, qnames, namespaces,
                   short_empty_elements, **kwargs):
    tag = elem.tag
    text = elem.text
    if tag is ET.Comment:
        write("<!--%s-->" % text)
    elif tag is ET.ProcessingInstruction:
        write("<?%s?>" % text)
    else:
        tag = qnames[tag]
        if tag is None:
            if text:
                write(_escape_cdata(text))
            for e in elem:
                _serialize_xml(write, e, qnames, None,
                               short_empty_elements=short_empty_elements)
        else:
            write("<" + tag)
            items = list(elem.items())
            if items or namespaces:
                if namespaces:
                    for v, k in sorted(namespaces.items(),
                                       key=lambda x: x[1]):  # sort on prefix
                        if k:
                            k = ":" + k
                        write(" xmlns%s=\"%s\"" % (
                            k,
                            _escape_attrib(v)
                            ))
                for k, v in items:
                    if isinstance(k, ET.QName):
                        k = k.text
                    if isinstance(v, ET.QName):
                        v = qnames[v.text]
                    else:
                        v = ET._escape_attrib(v)
                    write(" %s=\"%s\"" % (qnames[k], v))
            if text or len(elem) or not short_empty_elements:
                write(">")
                if text:
                    write(ET._escape_cdata(text))
                for e in elem:
                    _serialize_xml(write, e, qnames, None,
                                   short_empty_elements=short_empty_elements)
                write("</" + tag + ">")
            else:
                write(" />")
    if elem.tail:
        write(ET._escape_cdata(elem.tail))