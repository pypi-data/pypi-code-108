import datetime
import logging
from typing import List, Optional

from pystac import Asset, Collection, Extent, Item, MediaType, Summaries
from pystac.extensions.file import FileExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.label import LabelClasses, LabelExtension, LabelType
from pystac.extensions.scientific import ScientificExtension
from stactools.core import create
from stactools.core.io import ReadHrefModifier

from stactools.noaa_c_cap import Dataset, utils
from stactools.noaa_c_cap.constants import (COLLECTION_CITATION,
                                            COLLECTION_DESCRIPTION,
                                            COLLECTION_ID, COLLECTION_KEYWORDS,
                                            COLLECTION_PROVIDERS,
                                            COLLECTION_TITLE, FILE_VALUES,
                                            LABEL_CLASSES)

logger = logging.getLogger(__name__)


def create_collection(hrefs: Optional[List[str]] = None) -> Collection:
    """Creates a STAC Collection for all C-CAP data.

    Args:
        hrefs (Optional[str]): If provided, create a Collection for the provided
        HREFs. If not provided, use the network locations defined in
        `urllist-modres.txt`.
    """
    if not hrefs:
        hrefs = utils.urls()
    datasets = Dataset.from_hrefs(hrefs)
    items = [create_item_from_dataset(dataset) for dataset in datasets]
    extent = Extent.from_items(items)
    summaries = Summaries.empty()
    summaries.add("gsd", list(set(item.common_metadata.gsd for item in items)))
    summaries.add("label:classes", [{"classes": LABEL_CLASSES}])
    collection = Collection(id=COLLECTION_ID,
                            title=COLLECTION_TITLE,
                            description=COLLECTION_DESCRIPTION,
                            extent=extent,
                            keywords=COLLECTION_KEYWORDS,
                            providers=COLLECTION_PROVIDERS,
                            summaries=summaries)
    collection.add_items(items)

    item_assets = {}
    for item in items:
        for key, asset in item.get_assets().items():
            asset_as_dict = asset.to_dict()
            asset_as_dict.pop('href')
            if key not in item_assets:
                item_assets[key] = AssetDefinition(asset_as_dict)
            elif item_assets[key].to_dict() != asset_as_dict:
                logger.warning(f"Item Asset '{key}' does not match asset:\n"
                               f"item_asset={item_assets[key].to_dict()}\n"
                               f"asset={asset_as_dict}")

    item_assets_ext = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets_ext.item_assets = item_assets

    scientific = ScientificExtension.ext(collection, add_if_missing=True)
    scientific.citation = COLLECTION_CITATION

    return collection


def create_item(tiff_href: str,
                xml_href: Optional[str] = None,
                read_href_modifier: Optional[ReadHrefModifier] = None) -> Item:
    """Creates a STAC Item for the provided C-CAP tiff file.

    Args:
        tiff_href (str): The HREF pointing to the tiff file.
        xml_href (str): The HREF pointing to the xml file.
        read_href_modifier (Callable[[str], str]): A function to modify the read href for the file.

    Returns:
        Item: STAC Item object
    """
    return create_item_from_dataset(Dataset(tiff_href=tiff_href,
                                            xml_href=xml_href),
                                    read_href_modifier=read_href_modifier)


def create_item_from_dataset(
        dataset: Dataset,
        read_href_modifier: Optional[ReadHrefModifier] = None) -> Item:
    """Creates an item from a NOAA C-CAP dataset."""
    logger.info(f"Creating STAC item from {dataset.tiff_href}")
    item = create.item(dataset.tiff_href,
                       read_href_modifier=read_href_modifier)
    item.common_metadata.start_datetime = datetime.datetime(
        int(dataset.year), 1, 1, tzinfo=datetime.timezone.utc)
    item.common_metadata.end_datetime = datetime.datetime(
        int(dataset.year), 12, 31, tzinfo=datetime.timezone.utc)
    item.common_metadata.gsd = 30
    item.datetime = item.common_metadata.start_datetime

    label = LabelExtension.ext(item, add_if_missing=True)
    label.label_properties = None
    label.label_description = "Land cover classes"
    label.label_type = LabelType.RASTER
    label.label_classes = [
        LabelClasses.create(name='classes', classes=list(LABEL_CLASSES))
    ]

    data = item.assets.get('data')
    assert data
    data.media_type = MediaType.GEOTIFF

    file = FileExtension.ext(data, add_if_missing=True)
    file.values = FILE_VALUES

    if dataset.xml_href:
        item.add_asset(
            'metadata',
            Asset(dataset.xml_href,
                  media_type=MediaType.XML,
                  roles=['metadata']))
    return item
