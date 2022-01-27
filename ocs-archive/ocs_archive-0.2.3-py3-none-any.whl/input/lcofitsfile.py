from ocs_archive.input.fitsfile import FitsFile
from ocs_archive.input.file import File, FileSpecificationException
from ocs_archive.settings import settings


LETTER_TO_OBSTYPE = {
    'b': 'BIAS',
    'd': 'DARK',
    'f': 'SKYFLAT',
    'g': 'GUIDE',
    's': 'STANDARD',
    'w': 'LAMPFLAT',
    'x': 'EXPERIMENTAL'
}

class LcoFitsFile(FitsFile):
    def __init__(self, open_file: File, file_metadata: dict = None, blacklist_headers: tuple = settings.HEADER_BLACKLIST, required_headers: tuple = settings.REQUIRED_HEADERS):
        """LCO specific FitsFile format, provides some extra repair for broken headers from the filename."""
        super().__init__(open_file, file_metadata, blacklist_headers, required_headers)
        self._check_catalog()
        self._repair_configuration_type()
        self._repair_reduction_level()

    def _check_catalog(self):
        if '_cat' in self.open_file.basename:
            header_updates = {}
            headers = self.header_data.get_headers()
            if not headers.get(settings.CATALOG_TARGET_FRAME_KEY):
                # Check if the catalog file contains it's target frame, if not deduce it
                l1idcat = self.open_file.basename.replace('_cat', '')
                header_updates[settings.CATALOG_TARGET_FRAME_KEY] = l1idcat
            # set configuration type to CATALOG even though it's might be set to EXPOSE by the pipeline
            # TODO: pipeline should just create catalog files with correct keys
            header_updates[settings.CONFIGURATION_TYPE_KEY] = 'CATALOG'
            self.header_data.update_headers(header_updates)

    def _repair_configuration_type(self):
        conftype = self.header_data.get_configuration_type()
        if not conftype or conftype.strip() == 'UNKNOWN':
            try:
                headers = self.header_data.get_headers()
                name_parts = self.open_file.basename.split('-')
                conftype_letter = name_parts[4][0]
                is_nres = 'igl' in headers.get('ENCID', '') or (self.header_data.get_telescope_id() and 'igl' in self.header_data.get_telescope_id())
                if 'trace' == name_parts[0]:
                    conftype = 'TRACE'
                elif 'arc' == name_parts[0]:
                    conftype = 'ARC'
                elif 'bias' == name_parts[3]:
                    conftype = 'BIAS'
                elif 'bpm' == name_parts[3]:
                    conftype = 'BPM'
                elif conftype_letter == 'e':
                    if is_nres:
                        conftype = 'TARGET'
                    elif 'en' in name_parts[1]:
                        conftype = 'SPECTRUM'
                    else:
                        conftype = 'EXPOSE'
                elif conftype_letter == 'a':
                    if is_nres:
                        conftype = 'DOUBLE'
                    else:
                        conftype = 'ARC'
                elif conftype_letter in LETTER_TO_OBSTYPE:
                    conftype = LETTER_TO_OBSTYPE[conftype_letter]
                else:
                    # Failed to infer an configuration type for this filename
                    raise Exception()
                # Set the configuration type into the header
                self.header_data.update_headers({settings.CONFIGURATION_TYPE_KEY: conftype})
            except Exception:
                raise FileSpecificationException(f'{settings.CONFIGURATION_TYPE_KEY} is UNKNOWN and could not be inferred. Please manually correct it')

    def _repair_reduction_level(self):
        reduction_level = self.header_data.get_reduction_level()
        if not reduction_level:
            # TODO: Pipeline should write this value instead of
            # being inferred from the filename
            MAX_REDUCTION = 90
            MIN_REDUCTION = 0

            # remove the _cat extension from catalog files
            basename = self.open_file.basename.replace('_cat', '')

            if self.open_file.extension == '.tar.gz':
                self.header_data.update_headers({settings.REDUCTION_LEVEL_KEY: MAX_REDUCTION})
            else:
                try:
                    # lsc1m005-kb78-20151007-0214-x00
                    # extract reduction level at the position of 00
                    self.header_data.update_headers({settings.REDUCTION_LEVEL_KEY: int(basename[-2:])})
                except ValueError:
                    # Some filenames don't have this extension - return a sensible default
                    self.header_data.update_headers({settings.REDUCTION_LEVEL_KEY: MIN_REDUCTION})

    def _is_bpm_file(self):
        """Check if the file is a bad pixel mask using several LCO specific rules"""
        headers = self.header_data.get_headers()
        if self.header_data.get_configuration_type() == 'BPM' or headers.get('EXTNAME') == 'BPM':
            return True
        self.open_file.basename = self.open_file.basename.replace('_', '-')
        if self.open_file.basename.startswith('bpm-') or '-bpm-' in self.open_file.basename or self.open_file.basename.endswith('-bpm'):
            return True
        return False

    def get_filestore_path(self):
        if self._is_bpm_file():
            return '/'.join((self.header_data.get_site_id(), self.header_data.get_instrument_id(), 'bpm', self.open_file.basename)) + self.open_file.extension
        return super().get_filestore_path()