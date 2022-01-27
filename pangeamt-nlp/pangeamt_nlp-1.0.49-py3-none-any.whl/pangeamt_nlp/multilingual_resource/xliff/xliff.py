import re
from lxml import etree
from pangeamt_nlp.utils.guess_file_encoding import guess_file_encoding


class Xliff:
    XLIFF = '{*}xliff'
    TU = '{*}trans-unit'
    LANG_ATTRIBUTE = '{http://www.w3.org/XML/1998/namespace}lang'
    SEG_SOURCE = '{*}seg-source'
    SOURCE = '{*}source'
    TARGET = '{*}target'
    MRK = '{*}mrk'
    EXCLUED_TAGS = {}

    def __init__(self, file, encoding=None):
        self._file = file
        self._encoding = encoding
        if encoding is None:
            self._encoding = guess_file_encoding(self._file)

        self._version = self._detect_version()
        if self._version > 1.2:
            raise ValueError(f'Xliff version of file `{self._file}` > 1.2')

        self._num_trans_units = None

    def _detect_version(self):
        xliff_tag_parser = etree.XMLPullParser(tag=Xliff.XLIFF, events=['start'])
        with open(self._file, encoding=self._encoding) as f:
            for i, line in enumerate(f):
                if i == 0:
                    line = self.xml_version_2_xml_version_1(line)
                xliff_tag_parser.feed(line)
                for action, xliff in xliff_tag_parser.read_events():
                    return float(xliff.attrib['version'])

    def xml_version_2_xml_version_1 (self, text):
        # Replace xml version="2.0" to xml version="1" # xml 2.0 doesn't exist!!! but the okapi framework generate xliff with that version of xml...
        regex = r'(.*<\?xml[^>]*)(version="2.0")([^>]*\?>.*)'
        result = re.sub(regex,r'\1version="1.0"\3', text)
        return result



    def read(self, reader):
        yield from map(reader.read, self._read_raw())

    def _read_raw(self):
        parser = etree.XMLPullParser(tag=Xliff.TU)
        num_tu = 0
        previous_line_where_tu_detected = 0
        line_where_tu_detected = 0

        with open(self._file, encoding=self._encoding) as f:
            for num_line, line in enumerate(f):
                if num_line == 0:
                    line = self.xml_version_2_xml_version_1(line)

                # Feed the parser
                parser.feed(line)

                # Trans-unit extraction
                for action, tu in parser.read_events():
                    try:
                        previous_line_where_tu_detected = line_where_tu_detected
                        line_where_tu_detected = num_line
                        seg_source = tu.find(Xliff.SEG_SOURCE)

                        # Not segmented extraction
                        if seg_source is None:
                            result = {}
                            src = tu.find(Xliff.SOURCE)
                            src_lang = src.attrib[self.LANG_ATTRIBUTE]
                            result[src_lang] = src

                            tgts = tu.findall(Xliff.TARGET)
                            for tgt in tgts:
                                tgt_lang = tgt.attrib[self.LANG_ATTRIBUTE]
                                result[tgt_lang] = tgt
                            yield result

                        # Segmented extraction
                        else:
                            segs = []
                            src = tu.find(Xliff.SOURCE)
                            src_lang = src.attrib[self.LANG_ATTRIBUTE]
                            mkrs = seg_source.findall(f'{Xliff.MRK}[@mtype="seg"]')
                            for mkr in mkrs:
                                seg = {}
                                seg[src_lang] = mkr
                                segs.append(seg)

                            for tgt in tu.findall(self.TARGET):
                                tgt_lang = tgt.attrib[self.LANG_ATTRIBUTE]
                                for i, mkr in enumerate(tgt.findall(f'{Xliff.MRK}[@mtype="seg"]')):
                                    segs[i][tgt_lang] = mkr
                            yield from segs

                    except Exception as e:
                        raise ValueError(f"Error reading xliff {self._file} between line nº {previous_line_where_tu_detected} and line nº {line_where_tu_detected}. Error: {e}")

                    # Clear
                    tu.clear()

                    # Del element before
                    while tu.getprevious() is not None:
                        del tu.getparent()[0]

    def get_num_trans_units(self):
        if self._num_trans_units is None:
            with open(self._file, 'r', encoding=self._encoding) as f:
                parser = etree.XMLPullParser(tag=self.TU)
                self._num_trans_units = 0
                for i, line in enumerate(f):
                    if i == 0:
                        line = self.xml_version_2_xml_version_1(line)
                    parser.feed(line)
                    for _, tu in parser.read_events():
                        seg_source = tu.find(Xliff.SEG_SOURCE)
                        if seg_source is None:
                            self._num_trans_units += 1
                        else:
                            self._num_trans_units += len(seg_source.findall(f'{Xliff.MRK}[@mtype="seg"]'))
                        # Clear
                        tu.clear()
                        while tu.getprevious() is not None:
                            del tu.getparent()[0]
        return self._num_trans_units
    num_trans_units = property(get_num_trans_units)

    @staticmethod
    def seg_to_text(seg):
        return ''.join(Xliff.seg_text_iteraror(seg))

    # iter text from segment
    @staticmethod
    def seg_text_iteraror (node):
        if node.tag not in Xliff.EXCLUED_TAGS:
            if node.text is not None:
                yield node.text
            for child in node:
                if child.tag not in Xliff.EXCLUED_TAGS:
                    yield from Xliff.seg_text_iteraror(child)
                if child.tail is not None:
                    yield child.tail



