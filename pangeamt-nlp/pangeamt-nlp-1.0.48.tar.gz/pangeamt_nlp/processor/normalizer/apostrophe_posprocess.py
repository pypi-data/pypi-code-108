from typing import List
from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import string

class ApostrophePosprocess(NormalizerBase):
    NAME = "apostrophe_posprocess"

    DESCRIPTION_TRAINING = """"""

    DESCRIPTION_DECODING = """
        Remove spaces around apostrophe
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def correct_english_apostrophe(self, seg:Seg, list_of_apostrophe: List) -> None:
        list_of_punctuation = list(string.punctuation)
        for letter in list_of_apostrophe:
            seg.tgt = seg.tgt.replace(f' ’ {letter} ', f'’{letter} ')\
                             .replace(f'’ {letter} ', f'’{letter} ')
            for sign in list_of_punctuation:
                seg.tgt = seg.tgt.replace(f' ’ {letter}{sign} ', f'’{letter}{sign} ')\
                             .replace(f'’ {letter}{sign} ', f'’{letter}{sign} ')\
                             .replace(f' ’ {letter}{sign}', f'’{letter}{sign}')\
                             .replace(f'’ {letter}{sign}', f'’{letter}{sign}')
        

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang not in ['fr', 'es']:
            words = []
            if self.tgt_lang == 'en':
                list_of_apostrophe = ["m", "re", "s", "ve", "d", "ll", "t"]
                self.correct_english_apostrophe(seg, list_of_apostrophe)
            else:
                seg.tgt = seg.tgt.replace(' ’ ', '’')

