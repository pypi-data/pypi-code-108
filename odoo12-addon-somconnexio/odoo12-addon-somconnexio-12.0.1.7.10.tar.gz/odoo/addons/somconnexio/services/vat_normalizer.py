from stdnum.util import clean

CHARS_TO_CLEAN = " -."


class VATNormalizer:
    def __init__(self, vat):
        self.vat = vat or ""

    def normalize(self):
        self.vat = clean(self.vat, CHARS_TO_CLEAN).upper().strip()
        return self.vat

    def convert_spanish_vat(self):
        self.normalize()
        if self.vat[:2] != 'ES':
            self.vat = "ES{}".format(self.vat)
        return self.vat
