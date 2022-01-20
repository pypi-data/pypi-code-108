import os
from typing import Optional, Tuple
from pangeamt_nlp.multilingual_resource.multilingual_resource_base import (
    MultilingualResourceBase,
)


class Bilingual(MultilingualResourceBase):
    def __init__(
        self,
        file_1: str,
        file_2: str,
        file_1_encoding: Optional[str] = "utf-8",
        file_2_encoding: Optional[str] = "utf-8",
    ):

        super().__init__(MultilingualResourceBase.TYPE_BILINGUAL)

        self._file_1 = file_1
        self._file_2 = file_2

        self._file = (file_1, file_2)

        self._file_1_encoding = file_1_encoding
        self._file_2_encoding = file_2_encoding

        # Get language from ext
        ext_1 = os.path.splitext(self._file_1)[1]
        self._lang_1 = ext_1.replace(".", "")
        ext_2 = os.path.splitext(self._file_2)[1]
        self._lang_2 = ext_2.replace(".", "")

        self._num_trans_units = None

    def read(self, reader=None) -> Tuple[str, str]:
        if reader is not None:
            reader.initialize(self)

        with open(
            self._file_1, "r", encoding=self._file_1_encoding
        ) as src_file:
            with open(
                self._file_2, "r", encoding=self._file_2_encoding
            ) as tgt_file:
                num_line = 0
                while True:
                    text_1 = src_file.readline()
                    text_2 = tgt_file.readline()

                    if text_1 == "" or text_2 == "":
                        if text_1 != "" or text_2 != "":
                            raise ValueError(
                                f'Bilingual files "{self._file_1}" and "{self._file_2}" do not have the same number of lines'
                            )
                        else:
                            return

                    text_1_stripped = text_1.strip()
                    text_2_stripped = text_2.strip()

                    # if text_1_stripped == "":
                    #     raise ValueError(
                    #         f'Bilingual file "{self._file_1}" has an empty line at line {num_line}'
                    #     )
                    #
                    # if text_2_stripped == "":
                    #     raise ValueError(
                    #         f'Bilingual file "{self._file_2}" has an empty line at line {num_line}'
                    #     )

                    num_line += 1
                    if reader is None:
                        yield text_1_stripped, text_2_stripped
                    else:
                        yield reader.read(text_1_stripped, text_2_stripped)

    def get_num_trans_units(self):
        if self._num_trans_units is None:
            self._num_trans_units = 0
            with open(self._file_1, "rb") as src_file:
                with open(self._file_2, "rb") as tgt_file:
                    while True:
                        src = src_file.readline()
                        tgt = tgt_file.readline()
                        if src == b"" or tgt == b"":
                            if src != b"" or tgt != b"":
                                raise ValueError(
                                    f'Bilingual files "{self._file_1}" and "{self._file_2}" do not have the same number of lines'
                                )
                            else:
                                break
                        self._num_trans_units += 1
        return self._num_trans_units

    num_trans_units = property(get_num_trans_units)

    def get_lang_1(self):
        return self._lang_1

    lang_1 = property(get_lang_1)

    def get_lang_2(self):
        return self._lang_2

    lang_2 = property(get_lang_2)

    def get_file_1(self):
        return self._file_1

    file_1 = property(get_file_1)

    def get_file_2(self):
        return self._file_2

    file_2 = property(get_file_2)

    def get_file(self):
        return self._file

    file = property(get_file)
