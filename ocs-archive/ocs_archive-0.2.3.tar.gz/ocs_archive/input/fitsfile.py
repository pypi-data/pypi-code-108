from astropy.io import fits
import io
from contextlib import contextmanager

from ocs_archive.input.file import File, DataFile, FileSpecificationException
from ocs_archive.input.headerdata import HeaderData
from ocs_archive.settings import settings


class FitsFile(DataFile):
    # These are header keys that must contain integer values or None for archive validation
    INTEGER_TYPES = [
        settings.REQUEST_ID_KEY, settings.REQUESTGROUP_ID_KEY,
        settings.OBSERVATION_ID_KEY, settings.CONFIGURATION_ID_KEY
    ]

    def __init__(self, open_file: File, file_metadata: dict = None, blacklist_headers: tuple = settings.HEADER_BLACKLIST, required_headers: tuple = settings.REQUIRED_HEADERS):
        """Loads in fits file headers, then does some automatic cleanup and normalization of values."""
        super().__init__(open_file, file_metadata, blacklist_headers, required_headers)
        self._check_extension()
        self._remove_blacklist_headers(blacklist_headers)
        self._normalize_null_values()
        self._normalize_related_frames()

    def _remove_blacklist_headers(self, blacklist_headers: tuple):
        if '' not in blacklist_headers:
            # Always remove the empty string header since it causes issues
            self.header_data.remove_header('')
        for header in self.blacklist_headers:
            self.header_data.remove_header(header)

    def _normalize_null_values(self):
        header_updates = {}
        #  Sometimes keywords use N/A to mean null
        for k, v in self.header_data.get_headers().items():
            if v in settings.NULL_HEADER_VALUES:
                if k in self.INTEGER_TYPES:
                    header_updates[k] = None
                else:
                    header_updates[k] = ''
            # Catch None and NONE values for Integer type fields so they pass archive validation
            elif k in self.INTEGER_TYPES and ('NONE' in str(v).upper()):
                header_updates[k] = None
        self.header_data.update_headers(header_updates)

    def _normalize_related_frames(self):
        related_frame_keys = self.header_data.get_related_frame_keys()
        headers = self.header_data.get_headers()
        for key in related_frame_keys:
            filename = headers.get(key)
            if filename and filename != 'N/A':
                basename, extension = File.get_basename_and_extension(filename)
                if extension:
                    # Remove any extensions for the related frames, since the archive expects that
                    self.header_data.update_headers({key: basename})

    @contextmanager
    def get_fits(self):
        yield self.open_file.get_from_start()

    def _check_extension(self):
        if self.open_file.extension not in ['.fits', '.fits.fz']:
            raise FileSpecificationException(f'Fits files must have extension .fits or .fits.fz, not {self.open_file.extension}')

    def _is_valid_fits(self):
        try:
            with self.get_fits() as fits_file:
                with fits.open(io.BytesIO(fits_file.read()), mode='readonly') as hdu_list:
                    hdu_list.verify()
                return True
        except Exception:
            return False

    def _create_header_data(self, file_metadata: dict):
        if self._is_valid_fits():
            # Loop through each HDU and use the first header that passes validation as the dict representation
            with self.get_fits() as fits_file:
                with fits.open(io.BytesIO(fits_file.read()), mode='readonly') as hdulist:
                    for hdu in hdulist:
                        fits_dict = dict(hdu.header)
                        if file_metadata:
                            fits_dict.update(file_metadata)
                        if self._is_valid_file_metadata(fits_dict):
                            self.header_data = HeaderData(fits_dict)
                            return
                        else:
                            continue
                raise FileSpecificationException(
                    'Could not find required keywords in headers!')  # Missing one or more required headers
        else:
            # If there are no valid fits headers in the file, fall back on passed in metadata
            super()._create_header_data(file_metadata)

    def get_filestore_content_type(self):
        return 'image/fits'
