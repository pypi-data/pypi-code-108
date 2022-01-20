from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
from pangeamt_nlp.utils.strip_and_catch_white import strip_and_catch_white


class DetokBlanksSlashQuotes(NormalizerBase):
    NAME = "detok_blanks_norm"
    DESCRIPTION_TRAINING = """
    """
    DESCRIPTION_DECODING = """
          Remove spaces next to slashes and quotes
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def remove_blanks_between_extensions_and_name(self, seg: Seg) -> None:
        extensions = ['.vbs', '.png', '.jpg', ".csv"]
        s_list = seg.tgt.split()
        ini_len = len(s_list)
        i = 0
        last = 0
        rest = 0
        no_entry = True
        for ext in extensions:
            index = [i for i, s in enumerate(s_list) if ext in s]
            for ind in index:
                ind = ind - rest 
                aux = s_list[ind]
                i = ind
                no_entry = False
                while (i > 0 and not no_entry):
                    if s_list[i-1] == '_' or s_list[i-1] == '*':
                        aux = s_list[i-1] + aux
                        if i != 1 :
                            aux = s_list[i-2] + aux
                            i = i -1 
                        i = i-1
                    else:
                        last = i
                        no_entry = True
                p_list = s_list[:last] + s_list[ind+1:]
                p_list.insert(last, aux)
                s_list = p_list
                act_len = len(s_list)
                rest = ini_len - act_len
        seg.tgt = ' '.join(s_list)

    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = seg.tgt.replace(" / ", "/").replace(" ”", "”").\
            replace ("© ", "©").replace(" ™", "™").replace(" ®", "®").replace(" €", "€").\
            replace("http:// ", "http://").replace("https:// ", "https://").\
            replace("# ", "#").replace(" @ ", "@").replace("o ’ clock", "o’clock").replace("o’ clock", "o’clock").replace("m ²", "m²")
        if self.tgt_lang == 'tr':
            if seg.tgt[0] == "%":
                seg.tgt = seg.tgt.replace("% ", "%")
            
            else:
                seg.tgt = seg.tgt.replace("% ", " %")
        self.remove_blanks_between_extensions_and_name(seg)
            


