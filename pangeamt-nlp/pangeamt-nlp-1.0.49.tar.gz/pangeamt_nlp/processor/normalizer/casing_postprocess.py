from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg, SegCase
from sacremoses import MosesDetruecaser


class CasingPostprocess(NormalizerBase):
    NAME = "casing_postprocess"

    DESCRIPTION_TRAINING = """"""

    DESCRIPTION_DECODING = """
        Copy the casing of the source
    """

    LATIN_LANGS = [
        'es', 'fr', 'pt', 'it', 'ro', 'ca', 'ga', 'sc', 'oc', ' wa', 'co', 'an'
    ]
    NON_UPPER_LANGS = [
        'ja', 'zh', 'tw', 'ko', 'ar', 'hi', 'he', 'th', 'ka'
    ]

    PUNCTS_GENERAL = [
        "'", '"', "‘", '«', "“", '「', '『', '„', '»', '›', '‚', '‹',
        '-', '*', '{', '[', '#'
    ]

    PUNCTS_SPANISH = ['¿', "¡"]

    def __init__(self, src_lang: str, tgt_lang: str, apply_train=False) -> None:
        super().__init__(src_lang, tgt_lang)
        self._detruecaser = MosesDetruecaser()
        self.apply_train = apply_train

    def process_train(self, seg: Seg, apply_train=False) -> None:
        if apply_train:
            if seg.src_raw.isupper() and seg.tgt_raw.isupper():
                seg.src = seg.src.casefold()
                seg.tgt = seg.tgt.casefold()
        else:
            pass

    def process_src_decoding(self, seg: Seg) -> None:
        if seg.src_raw.isupper():
            seg.src = seg.src.lower()

    def process_tgt_decoding(self, seg: Seg) -> None:
        if segment_has_nonempty_values(seg):

            if not is_non_upper_lang(self.src_lang) and seg.src_case == SegCase.UPPER:
                if  self.tgt_lang == "tr":
                    seg.tgt = tr_upper(seg.tgt)

                else: 
                    seg.tgt = seg.tgt.upper()
            elif (
                is_en_or_latin(self.src_lang)
                and is_latin(self.tgt_lang)
            ):
                if seg.src_case == SegCase.LOWER:
                    if  self.tgt_lang == "tr":
                        seg.tgt = tr_lower(seg.tgt)

                    else: 
                        seg.tgt = seg.tgt.lower()
                else:
                    detruecased_tgt = " ".join(
                        self._detruecaser.detruecase(seg.tgt)
                    )
                    if seg.src_raw[0] not in CasingPostprocess.PUNCTS_GENERAL \
                            and seg.tgt[0] not in CasingPostprocess.PUNCTS_SPANISH:
                        seg.tgt = process_first_char_casing(
                            seg.src_raw, detruecased_tgt
                        )
                    elif len(seg.src_raw) > 1 and len(seg.tgt) > 1:
                        if seg.tgt[0] in CasingPostprocess.PUNCTS_SPANISH:
                            seg.tgt = seg.tgt[0] + process_first_char_casing(
                                seg.src_raw[:], seg.tgt[1:]
                            )
                        elif seg.tgt[0] in CasingPostprocess.PUNCTS_GENERAL:
                            seg.tgt = seg.tgt[0] + process_first_char_casing(
                                seg.src_raw[1:], seg.tgt[1:]
                            )


def is_non_upper_lang(lang: str):
    return lang in CasingPostprocess.NON_UPPER_LANGS


def segment_has_nonempty_values(segment: Seg) -> bool:
    return (
        is_not_empty(segment.src_raw)
        and is_not_empty(segment.src)
        and is_not_empty(segment.tgt)
    )


def is_not_empty(s: str) -> bool:
    return s.strip() != ""


def is_en_or_latin(lang: str):
    return lang == "en" or is_latin(lang)


def is_latin(lang: str):
    return lang in CasingPostprocess.LATIN_LANGS


def process_first_char_casing(src_raw: str, tgt: str):
    first_char = tgt[0]
    if src_raw[0].isupper():
        first_char = first_char.upper()
    elif src_raw[0].islower():
        first_char = first_char.casefold()
    return first_char + tgt[1:]


def tr_lower (string):
    lower_map = {ord(u'I'): u'ı',ord(u'İ'): u'i',}
    lower = string.translate(lower_map).lower()
    lower = lower.replace ('denım', 'denim')
    return lower

def tr_upper(string):
    upper_map = {ord(u'ı'): u'I', ord(u'i'): u'İ',}
    upper = string.translate(upper_map).upper()
    upper = upper.replace('DENİM', 'DENIM').replace('T-SHİRT', 'T-SHIRT').replace('TETRİS', 'TETRIS')
    return upper
