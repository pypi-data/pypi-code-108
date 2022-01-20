"""
Mixin for a WorkflowDataTaskBase subclass which implements fits data retrieval functionality
"""
from io import BytesIO
from pathlib import Path
from typing import Generator
from typing import Iterable
from typing import Tuple
from typing import Type
from typing import Union

from astropy.io import fits

from dkist_processing_common.models.fits_access import FitsAccessBase

tag_type_hint = Union[Iterable[str], str]


class FitsDataMixin:
    """
    Mixin for the WorkflowDataTaskBase to support fits r/w operations
    """

    def fits_data_read(
        self, tags: tag_type_hint
    ) -> Generator[Tuple[Path, fits.HDUList], None, None]:
        for path in self.read(tags=tags):
            yield path, self.fits_data_open(path)

    def fits_data_read_hdu(
        self, tags: tag_type_hint
    ) -> Generator[Tuple[Path, Union[fits.PrimaryHDU, fits.CompImageHDU]], None, None]:
        for path, hdul in self.fits_data_read(tags=tags):
            yield path, self.fits_data_extract_hdu(hdul=hdul)

    def fits_data_read_fits_access(
        self,
        tags: tag_type_hint,
        cls: Type[FitsAccessBase],
        auto_squeeze: bool = True,
    ) -> Generator[FitsAccessBase, None, None]:
        for path, hdu in self.fits_data_read_hdu(tags=tags):
            yield cls(hdu=hdu, name=str(path), auto_squeeze=auto_squeeze)

    @staticmethod
    def fits_data_extract_hdu(hdul: fits.HDUList) -> Union[fits.PrimaryHDU, fits.CompImageHDU]:
        if hdul[0].data is not None:
            return hdul[0]
        return hdul[1]

    @staticmethod
    def fits_data_open(path: Union[str, Path]) -> fits.HDUList:
        return fits.open(path)

    def fits_data_write(
        self,
        hdu_list: fits.HDUList,
        tags: tag_type_hint,
        relative_path: Union[Path, str, None] = None,
    ) -> Path:
        file_obj = BytesIO()
        hdu_list.writeto(file_obj, checksum=True)
        file_obj.seek(0)
        return self.write(file_obj=file_obj, tags=tags, relative_path=relative_path)
