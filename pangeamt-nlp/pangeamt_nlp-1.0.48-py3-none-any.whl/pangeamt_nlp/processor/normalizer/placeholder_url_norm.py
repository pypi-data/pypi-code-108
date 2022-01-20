import re
from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class PlaceholderUrlNorm(NormalizerBase):

    NAME = "placeholder_url_normalizer"

    DESCRIPTION_TRAINING = """
        Wrap URLs in placeholders. Empty for now.
    """

    DESCRIPTION_DECODING = """
        Wrap URLs in placeholders.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:

        super().__init__(src_lang, tgt_lang)

    def normalize(self, txt: str) -> str:
        """ Normalize placeholder URLs

        Parameters:
        txt (str): String to normalize

        Returns:
        str: Returns the string normalized

        """
        urls = re.findall('http[s]?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', txt)
        if len(urls) > 0:
            txt_norm = []
            count = 1
            for token in txt.split(" "):
                if token in urls:
                    txt_norm.append("(URL"+str(count)+":"+token+")")
                    count += 1
                else:
                    txt_norm.append(token)
            return (" ".join(txt_norm), urls)
        else:
            return (txt, [])

    def substitute(self, txt: str, entities: []) -> str:
        if "(URL" in txt:
            ids = re.findall('URL[1-99]:', txt)
            for i in range(len(ids)):
                txt=re.sub("\(URL"+str(i+1)+":.*?\)",entities[i],txt)
        return (txt)

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        seg.src, seg.src_entities = self.normalize(seg.src)

    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = self.substitute(seg.tgt, seg.src_entities)
