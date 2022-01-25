from ..sc_test_case import SCTestCase
from ...services.vat_normalizer import VATNormalizer


class VATNormalizerTests(SCTestCase):

    def test_convert_spanish_vat(self):
        vat = "74.011 656-m"
        normalized_vat = VATNormalizer(vat).convert_spanish_vat()

        self.assertEqual(
            normalized_vat,
            "ES74011656M"
        )

    def test_normalize_vat(self):
        vat = "fr-321.234.567.8  9"
        normalized_vat = VATNormalizer(vat).normalize()

        self.assertEqual(
            normalized_vat,
            "FR32123456789"
        )
