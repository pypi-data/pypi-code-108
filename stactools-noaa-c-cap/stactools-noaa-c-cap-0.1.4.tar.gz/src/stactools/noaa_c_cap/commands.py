import logging
import os
from tempfile import TemporaryDirectory
from typing import Optional, Tuple

import click
import requests
import stactools.core.utils.convert
from click.types import Choice
from pystac.catalog import CatalogType

from stactools.noaa_c_cap import stac, utils

logger = logging.getLogger(__name__)


def create_noaa_c_cap_command(cli):
    """Creates the stactools-noaa-c-cap command line utility."""

    @cli.group(
        "noaa-c-cap",
        short_help=("Commands for working with stactools-noaa-c-cap"),
    )
    def noaa_c_cap():
        pass

    @noaa_c_cap.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    @click.option('--href', '-h', multiple=True)
    @click.option('--directory',
                  '-d',
                  help='Directory containing NOAA C-CAP files')
    @click.option('--catalog-type',
                  type=Choice([
                      'ABSOLUTE_PUBLISHED', 'RELATIVE_PUBLISHED',
                      'SELF_CONTAINED'
                  ]),
                  default='ABSOLUTE_PUBLISHED')
    def create_collection_command(destination: str, href: Tuple[str],
                                  directory: Optional[str],
                                  catalog_type: CatalogType):
        """Creates a STAC Collection
        Args:
            destination (str): An HREF for the Collection JSON
        """
        hrefs = list(href)
        if directory:
            hrefs.extend(
                os.path.join(os.path.abspath(directory), file_name)
                for file_name in os.listdir(directory))
        collection = stac.create_collection(hrefs=hrefs)
        collection.catalog_type = catalog_type
        collection.normalize_and_save(destination)

    @noaa_c_cap.command("create-item", short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    @click.option('-x', '--xml', help='HREF to the metadata XML file.')
    @click.option('--cogify/--no-cogify',
                  default=False,
                  help=('Use a Cloud-Optimized GeoTIFF version '
                        'of the input file as the data asset.'))
    def create_item_command(source: str, destination: str, xml: Optional[str],
                            cogify: bool):
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Collection
            xml (str): HREF to the metadata XML file
            cogify (bool): Use a Cloud-Optimized GeoTIFF version of the source
            file as the data asset
        """
        if cogify:
            cog = os.path.join(os.path.dirname(destination),
                               os.path.basename(source))
            stactools.core.utils.convert.cogify(source, cog)
            source = cog
        item = stac.create_item(source, xml)
        item.save_object(dest_href=destination)

    @noaa_c_cap.command(
        "download",
        short_help="Download NOAA C-CAP data into a target directory")
    @click.argument("destination")
    @click.option('--cogify/--no-cogify',
                  help="Convert the .tifs to COGs after download",
                  default=False)
    def download_command(destination: str, cogify: bool) -> None:
        """Downloads the source data to a target directory.

        Args:
            destination (str): A local directory into which the data will downloaded.
        """
        os.makedirs(destination, exist_ok=True)
        with TemporaryDirectory() as temporary_directory:
            for url in utils.urls():
                file_name = os.path.basename(url)
                final_path = os.path.join(destination, file_name)
                print(f"Downloading {url} to {final_path}")
                download_to_temporary_directory = cogify and os.path.splitext(
                    file_name)[1] == '.tif'
                if download_to_temporary_directory:
                    download_path = os.path.join(temporary_directory,
                                                 file_name)
                else:
                    download_path = final_path
                with open(download_path, 'wb') as f:
                    response = requests.get(url, stream=True)
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                if download_to_temporary_directory:
                    stactools.core.utils.convert.cogify(
                        download_path, final_path)

    return noaa_c_cap
