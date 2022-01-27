import io
import hashlib
import unittest

from ocs_archive.input.file import File, EmptyFile


class TestFile(unittest.TestCase):

    def test_get_basename_and_extension(self):
        file1 = EmptyFile('/archive/coj/kb84/20160325/raw/coj0m405-kb84-20160325-0095-e00.fits')
        self.assertEqual('coj0m405-kb84-20160325-0095-e00', file1.basename)
        self.assertEqual('.fits', file1.extension)

        file2 = EmptyFile('/archive/coj/kb84/20160325/raw/coj0m405-kb84-20160325-0095-e00.fits.fz')
        self.assertEqual('coj0m405-kb84-20160325-0095-e00', file2.basename)
        self.assertEqual('.fits.fz', file2.extension)

    def test_get_file_length(self):
        with io.BytesIO(b'1234567890') as fileobj:
            file = File(fileobj, 'some_fits.fits.fz')
            self.assertEqual(len(file), 10)

    def test_get_file_from_start(self):
        with io.BytesIO(b'1234567890') as fileobj:
            fileobj.read()
            file = File(fileobj, 'some_fits.fits.fz')
            file.fileobj.read()  # Go to end of file
            self.assertEqual(file.fileobj.tell(), 10)
            self.assertEqual(file.get_from_start().tell(), 0)

    def test_md5(self):
        # Make sure that md5 is computed from the start of the fileobj, even after having been read
        bstring = b'1234567890'
        md5bstring = hashlib.md5(bstring).hexdigest()
        with io.BytesIO(b'1234567890') as fileobj:
            file = File(fileobj)
            md51 = file.get_md5()
            file.fileobj.read()
            md52 = file.get_md5()
            self.assertEqual(md51, md52)
            self.assertEqual(md5bstring, md51)
