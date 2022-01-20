from lxml import etree
import datetime


class TmxWriter:
    def __init__(self,
                 file_path,
                 src_lang,
                 admin_lang = 'en',
                 seg_type='sentence',
                 otmf='Undefined',
                 data_type = "unknown" ):
        self._filePath = file_path
        self._src_lang = src_lang
        self._admin_lang = admin_lang
        self._seg_type = seg_type
        self._otmf = otmf
        self._data_type = data_type
        self._creation_date =  datetime.datetime.now()
        self._notes = []

    def add_note(self, note):
        self._notes.append(note)

    def create_tu(self):
        return self._tu

    def __enter__(self):
        self._file_handler = open(self._filePath, 'w', encoding='utf-8')
        self._tu = Tu(self._file_handler)
        header = '<?xml version="1.0" encoding="utf-8" ?>\n'
        header += '<tmx version="1.4">'

        header_tag = etree.Element('header', attrib={
            'creationtool':         'Pangeamt-nlp',
            'creationtoolversion':  '0.5',
            'segtype':              self._seg_type,
            'o-tmf':                self._otmf,
            'datatype':             self._data_type,
            'srclang':              self._src_lang,
            'adminlang':            self._admin_lang,
            'creationdate':         str(self._creation_date),
        })

        for note in self._notes:
            note_tag = etree.Element('note')
            note_tag.text = note
            header_tag.append(note_tag)

        pretty_header_tag = '\n' + etree.tostring(header_tag, pretty_print=True, encoding='unicode')
        pretty_header_tag = '\t'.join(pretty_header_tag.splitlines(True))

        header += pretty_header_tag
        header += '\t<body>\n'
        self._file_handler.write(header)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        footer = '\t</body>\n'
        footer += '</tmx>\n'
        self._file_handler.write(footer)
        self._file_handler.close()

class Tu:
    TYPE_TEXT = 0
    TYPE_XML = 1

    def __init__(self, file_handler):
        self._file_handler = file_handler
        self._tuvs = []

    def write(self, seg, lang):
        #TODO accept XML
        self._tuvs.append((Tu.create_seg_from_text(seg), lang))

    @staticmethod
    def create_seg_from_text(seg):
        elem =  etree.XML('<seg></seg>')
        elem.text = seg
        seg_unicode = etree.tostring(elem, encoding='unicode')
        return seg_unicode

    def __enter__(self):
        # Emtpy tuvs
        self._tuvs = []
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        self._file_handler.write('\t\t<tu>\n')
        tuvs = ''
        for seg, lang in self._tuvs:
            tuvs +=  '\t\t\t<tuv xml:lang="' + lang + '">\n'
            tuvs += '\t\t\t\t' + seg + '\n'
            tuvs += '\t\t\t</tuv>\n'
        self._file_handler.write(tuvs)
        self._file_handler.write('\t\t</tu>\n')
