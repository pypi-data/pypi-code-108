import json
import re
from typing import Union, Optional
from pangeamt_nlp.utils.raise_exception_if_file_not_found import raise_exception_if_file_not_found
from pangeamt_nlp.utils.raise_exception_if_file_found import raise_exception_if_file_found
from pangeamt_nlp.multilingual_resource.multilingual_resource_base import MultilingualResourceBase
from pangeamt_nlp.multilingual_resource.af.af_header import AfHeader
from pangeamt_nlp.multilingual_resource.af.af_reader import AfReader


class Af(MultilingualResourceBase):
    SEP = '|||'
    HEADER_SEP = '###\n'

    def __init__(self, file):
        super().__init__(MultilingualResourceBase.TYPE_AF)
        raise_exception_if_file_not_found(file)
        self._file = file
        self._header = AfHeader.create_from_json(Af.read_header(file))
        self._num_trans_units = None
        self._num_words_units = None
        self._num_chars_units = None
        self._writer = AfWriter(self._file)

    @staticmethod
    def new(file:str,
            left_lang=None,
            left_translator=None,
            left_translation_type=None,
            right_lang=None,
            right_translator=None,
            right_translation_type=None,
            corpus_file=None,
            corpus_name=None,
            corpus_domain=None):

        raise_exception_if_file_found(file)

        with open(file, 'w', encoding='utf-8') as f:
            header = AfHeader(left_lang,
                              left_translator,
                              left_translation_type,
                              right_lang,
                              right_translator,
                              right_translation_type,
                              corpus_file,
                              corpus_name,
                              corpus_domain)
            f.write(header.to_string())
        return Af(file)

    def read(self, reader=None):
        if reader is not None:
            reader.initialize(self)
        header_sep_found = False
        with open(self._file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if not header_sep_found:
                    if line == Af.HEADER_SEP:
                        header_sep_found = True
                    continue
                line = line.strip()
                parts = line.split(self.SEP)
                try:
                    left = parts[1]
                    right = parts[2]
                except:
                    raise ValueError(f"Invalid line `{i+1}`")
                if reader:
                    yield reader.read(left, right)
                else:
                    yield left, right

    @staticmethod
    def read_header(file: str):
        header = ''
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                if line != Af.HEADER_SEP:
                    header += line
                else:
                    return json.loads(header)
            raise HeaderSepNotFoundException(file)

    def get_header(self):
        return self._header
    header = property(get_header)

    def get_file(self):
        return self._file
    file = property(get_file)

    def get_num_trans_units(self):
        if self._num_trans_units is None:
            header_sep_found = False
            num = 0
            with open(self._file, 'rb') as f:
                for line in f:
                    if not header_sep_found:
                        line = line.decode('utf-8')
                        if line == Af.HEADER_SEP:
                            header_sep_found = True
                        continue
                    num += 1
            return num
        return self._num_trans_units
    num_trans_units = property(get_num_trans_units)

    def get_num_chars_units(self):
        if self._num_chars_units is None:
            header_sep_found = False
            num = 0
            with open(self._file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not header_sep_found:
                        if line == Af.HEADER_SEP:
                            header_sep_found = True
                        continue
                    line_split = line.split('|||')
                    num += len(line_split[1].strip()) + len(line_split[2].strip())
            return num
        return self._num_chars_units
    num_chars_units = property(get_num_chars_units)

    def get_num_words_units(self):
        if self._num_words_units is None:
            header_sep_found = False
            num = 0
            with open(self._file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not header_sep_found:
                        if line == Af.HEADER_SEP:
                            header_sep_found = True
                        continue
                    line_split = line.split('|||')
                    num += len(line_split[1].strip().split(' ')) + len(line_split[2].strip().split(' '))
            return num
        return self._num_words_units
    num_words_units = property(get_num_words_units)

    def get_writer(self):
        return self._writer
    writer = property(get_writer)

    @staticmethod
    def triangulate(af1: Union["Af", str], af2: Union["Af", str], output_file: Optional[str] = "auto"):
        # Create afs
        af1 = Af(af1) if type(af1) is str else af1
        af2 = Af(af2) if type(af2) is str else af2

        # Pivot language
        af1_langs = {af1.header.left.lang, af1.header.right.lang}
        af2_langs = {af2.header.left.lang, af2.header.right.lang}
        shared_langs = list(af1_langs & af2_langs)
        if len(shared_langs) != 1:
            raise PivotLanguageNotFound(af1, af2)
        pivot_lang = shared_langs[0]

        # Other languages
        af1_other_lang = [x for x in af1_langs if x != pivot_lang][0]
        af2_other_lang = [x for x in af2_langs if x != pivot_lang][0]

        # Extract af1 data
        af1_data = {}
        af1_reader = AfReader(src_lang=pivot_lang, tgt_lang=af1_other_lang)
        for src, tgt in af1.read(af1_reader):
            af1_data[src] = tgt

        output_data = []
        af2_reader = AfReader(src_lang=pivot_lang, tgt_lang=af2_other_lang)
        for src, tgt in af2.read(af2_reader):
            if src in af1_data:
                output_data.append((af1_data[src], tgt))

        if output_data and output_file is not None:
            standard_filename_pattern = r'_[a-z]{2}(_[a-z]{2})*-[a-z]{2}(_[a-z]{2})*\.af$'
            if output_file == 'auto':
                if not re.search(standard_filename_pattern, af1.file):
                    raise ValueError("af1 filename don't match standart pattern")
                base_new_name = re.sub(standard_filename_pattern, '', af1.file)
                output_file = f"{base_new_name}_triangulated_{af1_other_lang}-{af2_other_lang}.af"

            # Get header part for  lang != pivot
            af1_other_lang_header_part = af1.header.left if af1_other_lang == af1.header.left.lang else af1.header.right
            af2_other_lang_header_part = af2.header.left if af2_other_lang == af2.header.left.lang else af2.header.right

            # Corpus
            corpus_name = af1.header.corpus.name if af1.header.corpus.name == af2.header.corpus.name else None
            corpus_file = af1.header.corpus.file if af1.header.corpus.file == af2.header.corpus.file else None
            corpus_domain = af1.header.corpus.domain if af1.header.corpus.domain == af2.header.corpus.domain else None

            # Create new af
            af3 = Af.new(
                output_file,
                left_lang=af1_other_lang,
                left_translator=af1_other_lang_header_part.translator,
                left_translation_type=af1_other_lang_header_part.translation_type,
                right_lang=af2_other_lang,
                right_translator=af2_other_lang_header_part.translator,
                right_translation_type=af2_other_lang_header_part.translation_type,
                corpus_file=corpus_file,
                corpus_name=corpus_name,
                corpus_domain=corpus_domain
            )

            # Write
            with af3.writer as w:
                for i, (src, tgt) in enumerate(output_data):
                    w.write(i, src, tgt)
        return len(output_data)




class AfWriter:
    def __init__(self, file: str):
        self._file = file
        self._file_handler = None

    def __enter__(self):
        self._file_handler = open(self._file, 'a', encoding='utf-8')
        return self

    def __exit__(self, type, value, tb):
        self._file_handler.close()
        self._file_handler = None

    def write(self, id, left, right):
        self._file_handler.write(str(id) + Af.SEP + left + Af.SEP + right + '\n')

    def write_raw(self, line):
        self._file_handler.write(line)


class PivotLanguageNotFound(Exception):
    def __init__(self, af1, af2):
        super().__init__(f"Pivot language not found between `{af1.file}` and `{af2.file}`")


class HeaderSepNotFoundException:
    def __init__(self, file: str):
        super().__init__(f'Af header sep `{Af.SEP.strip()}`not found in {file} ')

