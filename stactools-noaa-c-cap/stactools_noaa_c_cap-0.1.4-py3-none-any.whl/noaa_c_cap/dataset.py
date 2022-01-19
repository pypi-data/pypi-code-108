import logging
import os.path
from typing import List, Optional

logger = logging.getLogger(__name__)


class Dataset:
    """A NOAA C-CAP dataset.

    Could be CONUS, could be somewhere else. Always has a tiff file, can have XML metadata.
    """
    tiff_href: str
    year: str
    location: str
    xml_file_name: Optional[str]
    xml_href: Optional[str]
    classes: List[str]

    @classmethod
    def from_hrefs(cls, hrefs: List[str]) -> List['Dataset']:
        """Creates one or more datasets from a list of hrefs.

        Does the work of looking through the HREFs to associate tifs with xml metadata.
        """
        datasets = []
        for tif_href in (href for href in hrefs
                         if os.path.splitext(href)[1] == '.tif'):
            dataset = Dataset(tif_href)
            if dataset.xml_file_name:
                xml_href = next(
                    (href for href in hrefs
                     if os.path.basename(href) == dataset.xml_file_name), None)
                if xml_href:
                    dataset.xml_href = xml_href
                else:
                    logger.warn(
                        f"Could not find XML metadata file for {tif_href}")
            datasets.append(dataset)
        return datasets

    def __init__(self, tiff_href: str, xml_href: Optional[str] = None):
        """Creates a new dataset for a GeoTIFF."""
        self.tiff_href = tiff_href
        self.xml_href = xml_href

        file_name = os.path.basename(tiff_href)
        parts = file_name.split('_')
        if len(parts) < 2:
            raise ValueError(f"Invalid NOAA C-CAP file name: {file_name}")
        self.location = parts[0]
        self.year = parts[1]
        if self.location == 'conus':
            self.xml_file_name: Optional[str] = f"CCAP_Parent_{self.year}.xml"
        elif self.location == 'hi':
            self.xml_file_name = None
        elif self.location == 'pr':
            self.xml_file_name = f"{self.year}_puerto_rico_ccap.xml"
