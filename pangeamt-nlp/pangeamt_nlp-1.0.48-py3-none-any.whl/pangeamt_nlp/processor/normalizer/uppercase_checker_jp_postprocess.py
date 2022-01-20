from sacremoses import MosesTokenizer as _MosesTokenizer
from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import string


class UppercaseCheckerJapanesePostprocess(NormalizerBase):
    NAME = "uppercase_checker_jp_postprocess"

    DESCRIPTION_TRAINING = ""

    DESCRIPTION_DECODING = """
            Transform English words that appear in the Japanese source to the correct lettering
        """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)
        self._mtk = _MosesTokenizer(tgt_lang)

    def get_no_cjk_word(self, src_text: str) -> str:
        list_words = []
        word = ""
        for i, char in enumerate(src_text):
            if char in list(string.ascii_uppercase) or char.isnumeric() or char == '-' or (len(src_text) > i + 1 and src_text[i].islower() and src_text[i+1].isupper()):
                #if char in list(string.ascii_uppercase) or char.isnumeric() or char == '-' or (src_text[i].islower() and len(src_text) > i + 1 and src_text[i + 1].isupper()):
                word += char
            elif char == " " or not char in list(string.ascii_uppercase) or char in string.punctuation:
                if word != "":
                    list_words.append(word)
                    word = ""
        return list_words

    def check_ref(self, seg: Seg) -> str:
        words = self.get_no_cjk_word(seg.src)
        tok_tgt_mt = self._mtk.tokenize(seg.tgt, escape=True)
        tgt_mt_text_out = seg.tgt
        for i, word in enumerate(words):
            if word.lower() in tok_tgt_mt:
                tgt_mt_text_out = (tgt_mt_text_out.replace(word.lower(), word))
            elif word[0].upper()+word[1:].lower() in tok_tgt_mt:
                tgt_mt_text_out = (tgt_mt_text_out.replace(word[0].upper()+word[1:].lower(), word))
            elif word[0:].upper() in tok_tgt_mt and word[0].islower():
                tgt_mt_text_out = (tgt_mt_text_out.replace(word[0:].upper(), word))
            elif len(words)>i+1 and word.lower()+words[i+1].lower() in tgt_mt_text_out and not word.isnumeric() and not words[i+1].isnumeric():
                tgt_mt_text_out = (tgt_mt_text_out.replace(word.lower()+words[i+1].lower(), word+" "+words[i+1]))
            else:
                for j, c in enumerate(word):
                    if c.isnumeric():
                        word2 = word.replace(c, "")
                        if word2.lower() in tok_tgt_mt:
                            tgt_mt_text_out = (tgt_mt_text_out.replace(word2.lower(), word2))
                        elif len(words)>i+1 and word2.lower()+words[i+1].lower() in tgt_mt_text_out and not word2.isnumeric() and not words[i+1].isnumeric():
                            tgt_mt_text_out = (tgt_mt_text_out.replace(word2.lower()+words[i+1].lower(), word2+" "+words[i+1]))
        return tgt_mt_text_out

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.src_lang == 'ja' and self.tgt_lang == "en":
            seg.tgt = self.check_ref(seg)

