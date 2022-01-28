import unittest

import lightkurve

from lcbuilder.constants import CUTOUT_SIZE
from lcbuilder.photometry.aperture_extractor import ApertureExtractor


class TestsApertures(unittest.TestCase):
    def test_from_boolean_mask(self):
        tpfs = lightkurve.search_targetpixelfile(target="TIC 251848941", cadence=120, author="SPOC")\
            .download_all()
        apertures = {}
        for tpf in tpfs:
            apertures[tpf.sector] = ApertureExtractor.from_boolean_mask(tpf.pipeline_mask, tpf.column, tpf.row)
        self.assertEquals(19, len(apertures[2]))
        self.assertTrue(any(([649, 171] == x).all() for x in apertures[2]))
        self.assertTrue(any(([649, 172] == x).all() for x in apertures[2]))
        self.assertTrue(any(([650, 170] == x).all() for x in apertures[2]))
        self.assertTrue(any(([650, 171] == x).all() for x in apertures[2]))
        self.assertTrue(any(([650, 172] == x).all() for x in apertures[2]))
        self.assertTrue(any(([650, 173] == x).all() for x in apertures[2]))
        self.assertTrue(any(([650, 174] == x).all() for x in apertures[2]))
        self.assertTrue(any(([651, 170] == x).all() for x in apertures[2]))
        self.assertTrue(any(([651, 171] == x).all() for x in apertures[2]))
        self.assertTrue(any(([651, 172] == x).all() for x in apertures[2]))
        self.assertTrue(any(([651, 173] == x).all() for x in apertures[2]))
        self.assertTrue(any(([651, 174] == x).all() for x in apertures[2]))
        self.assertTrue(any(([652, 170] == x).all() for x in apertures[2]))
        self.assertTrue(any(([652, 171] == x).all() for x in apertures[2]))
        self.assertTrue(any(([652, 172] == x).all() for x in apertures[2]))
        self.assertTrue(any(([652, 173] == x).all() for x in apertures[2]))
        self.assertTrue(any(([653, 171] == x).all() for x in apertures[2]))
        self.assertTrue(any(([653, 172] == x).all() for x in apertures[2]))
        self.assertTrue(any(([653, 173] == x).all() for x in apertures[2]))
        self.assertEquals(15, len(apertures[29]))
        self.assertTrue(any(([1133, 142] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1133, 143] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1133, 144] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1133, 145] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1134, 141] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1134, 142] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1134, 143] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1134, 144] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1134, 145] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1135, 142] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1135, 143] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1135, 144] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1135, 145] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1136, 143] == x).all() for x in apertures[29]))
        self.assertTrue(any(([1136, 144] == x).all() for x in apertures[29]))

    def test_from_pixels_to_boolean_mask(self):
        apertures = {2: [[649, 171], [649, 172], [650, 170], [650, 171], [650, 172], [650, 173], [650, 174],
                         [651, 170], [651, 171], [651, 172], [651, 173], [651, 174], [652, 170], [652, 171], [652, 172],
                         [652, 173], [653, 171], [653, 172], [653, 173]],
                     29: [[1133, 142], [1133, 143], [1133, 144], [1133, 145], [1134, 141], [1134, 142], [1134, 143],
                          [1134, 144], [1134, 145], [1135, 142], [1135, 143], [1135, 144], [1135, 145], [1136, 143],
                          [1136, 144]]}
        tpfs = lightkurve.search_targetpixelfile(target="TIC 251848941", cadence=120, author="SPOC") \
            .download_all(cutout_size=CUTOUT_SIZE)
        self.assertTrue(False not in (ApertureExtractor.from_pixels_to_boolean_mask(apertures[2], tpfs[0].column, tpfs[0].row, CUTOUT_SIZE, CUTOUT_SIZE) == tpfs[0].pipeline_mask))
        self.assertTrue(False not in (ApertureExtractor.from_pixels_to_boolean_mask(apertures[29], tpfs[1].column, tpfs[1].row, CUTOUT_SIZE, CUTOUT_SIZE) == tpfs[1].pipeline_mask))

    def test_cyclic_conversion(self):
        tpfs = lightkurve.search_targetpixelfile(target="TIC 251848941", cadence=120, author="SPOC") \
            .download_all(cutout_size=CUTOUT_SIZE)
        for tpf in tpfs:
            self.assertTrue((tpf.pipeline_mask == ApertureExtractor.from_pixels_to_boolean_mask(
                ApertureExtractor.from_boolean_mask(tpf.pipeline_mask, tpf.column, tpf.row), tpf.column, tpf.row,
                CUTOUT_SIZE, CUTOUT_SIZE)).all())


if __name__ == '__main__':
    unittest.main()
