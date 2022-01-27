import tarfile
from contextlib import contextmanager

from ocs_archive.input.file import FileSpecificationException
from ocs_archive.input.fitsfile import FitsFile


class TarWithFitsFile(FitsFile):
    def _check_extension(self):
        if self.open_file.extension not in ['.tar', '.tar.gz']:
            raise FileSpecificationException(f'Tar with Fits files must have extension .tar or .tar.gz, not {self.file.extension}')

    @staticmethod
    def _get_meta_file_from_targz(tarfileobj):
        for member in tarfileobj.getmembers():
            if any(x in member.name for x in ['.fits', '.fits.fz']) and member.isfile():
                return tarfileobj.extractfile(member)
        raise FileSpecificationException('Tar file missing meta fits!')

    @contextmanager
    def get_fits(self):
        """
        Return the fits file associated with this file.

        Generally this just the fileobj itself, but certain spectral data must have their
        fits files extracted. Use this as a context manager.
        """
        fits_file, tar_file = None, None
        try:
            tar_file = tarfile.open(fileobj=self.open_file.get_from_start(), mode='r')
            fits_file = self._get_meta_file_from_targz(tar_file)
            yield fits_file

        finally:
            if tar_file and fits_file:
                # The fits file object came from the tar file extraction, and must be closed
                fits_file.close()
            if tar_file:
                tar_file.close()

    def get_filestore_content_type(self):
        return 'application/x-tar'
