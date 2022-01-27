class DatasetReader:
    def __init__(self, tmx_reader = None, af_reader = None, bilingual_reader = None):
        self._tmx_reader = tmx_reader
        self._af_reader = af_reader
        self._bilingual_reader = bilingual_reader

    def get_tmx_reader(self):
        return self._tmx_reader
    tmx_reader = property(get_tmx_reader)

    def get_af_reader(self):
        return self._af_reader
    af_reader = property(get_af_reader)


    def get_bilingual_reader(self):
        return self._bilingual_reader
    bilingual_reader = property(get_bilingual_reader)
