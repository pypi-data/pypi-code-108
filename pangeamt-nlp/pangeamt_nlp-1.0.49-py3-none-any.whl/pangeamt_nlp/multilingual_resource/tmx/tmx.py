import logging
import os
from lxml import etree
from pangeamt_nlp.utils.guess_file_encoding import guess_file_encoding
from pangeamt_nlp.multilingual_resource.multilingual_resource_base import MultilingualResourceBase

class Tmx(MultilingualResourceBase):
    DEFAULT_LOCALE_ATTRIB = '{http://www.w3.org/XML/1998/namespace}lang'
    ALTERNATIVE_LOCALE_ATTRIB = 'lang'
    TU = 'tu'
    TUV = 'tuv'
    SEG = 'seg'
    TUV_TAGS =   {'bpt','ept','hi','it','ph', 'sub'}
    EXCLUED_TAGS =  {'bpt','ept', 'it', 'ph'}

    def __init__(self, file:str, encoding= None):
        super().__init__(MultilingualResourceBase.TYPE_TMX)
        # Tmx
        self._file = file

        # Encoding
        if encoding is None:
            self._encoding = guess_file_encoding(self._file)
        else:
            self._encoding = encoding

        self._num_trans_units = None
        self._num_words_units = None

    def read(self, reader):
        with open(self._file, encoding=self._encoding) as f:
            # Pull parser
            parser = etree.XMLPullParser(tag=Tmx.TU)

            locale_attribute = Tmx.DEFAULT_LOCALE_ATTRIB

            num_tu = 0
            previous_line_where_tu_detect = 0
            line_where_tu_detected = 0

            for num_line, line in enumerate(f):
                if num_line < 5:
                    # Lxml can't read utf-8-sig
                    line = line.replace('encoding="utf-8-sig"', 'encoding="utf-8"')
                parser.feed(line)

                for action, tu in parser.read_events():
                    # Line involved for error handling
                    previous_line_where_tu_detect = line_where_tu_detected
                    line_where_tu_detected = num_line

                    num_tu += 1
                    # Detect locale attribute type. We assume that it will not change :(
                    if num_tu == 1:
                        if tu.find(Tmx.TUV + '[@'+ locale_attribute + ']') is None:
                            locale_attribute = Tmx.ALTERNATIVE_LOCALE_ATTRIB

                    # Extract seg by local
                    tuvs = tu.findall(Tmx.TUV)
                    segs_by_locale = {}
                    for tuv in tuvs:
                        locale = tuv.get(locale_attribute)
                        seg = tuv.find(Tmx.SEG) # One seg per TUV (Tmx spec)
                        segs_by_locale[locale] = seg

                    try:
                        yield reader.read(segs_by_locale)
                    except Exception as e:
                        raise ValueError(
                            f'Tmx extraction error "{self._file}" between lines {previous_line_where_tu_detect} and {line_where_tu_detected}. ' + str(e))

                    # Clear
                    tu.clear()
                    while tu.getprevious() is not None:
                        del tu.getparent()[0]
        return

    def get_num_trans_units(self):
        if self._num_trans_units is None:
            with open(self._file, 'r', encoding=self._encoding) as f:
                parser = etree.XMLPullParser(tag=Tmx.TU)
                self._num_trans_units = 0
                for num_line, line in enumerate(f):
                    if num_line < 5:
                        # Lxml can't read utf-8-sig
                        line = line.replace('encoding="utf-8-sig"', 'encoding="utf-8"')
                    parser.feed(line)
                    for action, tu in parser.read_events():
                        self._num_trans_units += 1
                        while tu.getprevious() is not None:
                            del tu.getparent()[0]
        return self._num_trans_units
    num_trans_units = property(get_num_trans_units)

    def get_num_words_units(self):
        if self._num_words_units is None:
            with open(self._file, 'r', encoding=self._encoding) as f:
                parser = etree.XMLPullParser(tag=Tmx.SEG)
                self._num_words_units  = 0
                for num_line, line in enumerate(f):
                    if num_line < 5:
                        # Lxml can't read utf-8-sig
                        line = line.replace('encoding="utf-8-sig"', 'encoding="utf-8"')
                    parser.feed(line)
                    # print(parser.read_events())
                    for action, segment in parser.read_events():
                        # print(segment.getparent)
                        self._num_words_units += 1
                        while segment.getprevious() is not None:
                            del segment.getparent()[0]
        return self._num_words_units
    num_words_units = property(get_num_words_units)

    # get text from segment
    @staticmethod
    def seg_to_text(seg):
        return ''.join(Tmx.seg_text_iteraror(seg))

    # iter text from segment
    @staticmethod
    def seg_text_iteraror (node):
        if node.tag not in Tmx.EXCLUED_TAGS:
            if node.text is not None:
                yield node.text
            for child in node:
                if child.tag not in Tmx.EXCLUED_TAGS:
                    yield from Tmx.seg_text_iteraror(child)
                if child.tail is not None:
                    yield child.tail

    def get_file(self):
        return self._file
    file = property(get_file)





