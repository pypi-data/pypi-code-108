from pangeamt_nlp.multilingual_resource.dataset.dataset_reader import DatasetReader
from pangeamt_nlp.multilingual_resource.af.af_reader import AfReader
from pangeamt_nlp.multilingual_resource.bilingual.bilingual_reader import BilingualReader
from pangeamt_nlp.multilingual_resource.tmx.tmx_reader_bilingual import TmxReaderBilingualText

class DatasetReaderBilingual(DatasetReader):
    def __init__(self, src_lang, tgt_lang):
        super().__init__(
            tmx_reader=TmxReaderBilingualText(src_lang, tgt_lang),
            af_reader=AfReader(src_lang, tgt_lang),
            bilingual_reader=BilingualReader(src_lang, tgt_lang)
        )


