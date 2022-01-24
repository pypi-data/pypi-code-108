# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Dataset for prediction."""

import json
import os
import time

from torch.utils.data import Dataset
from torchvision.transforms import Compose
from torch.tensor import Tensor
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.utils import _read_image, _read_image_dimensions, _validate_image_exists
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.common.tiling_dataset_element import TilingDatasetElement
from azureml.automl.dnn.vision.common.tiling_utils import get_tiles, validate_tiling_settings
from azureml.automl.dnn.vision.object_detection.common.constants import DatasetFieldLabels
from azureml.core import Dataset as AmlDataset
from azureml.core import Workspace
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException
from typing import TypeVar, List, Any, Optional, Iterable, Tuple, cast, Dict

T_co = TypeVar('T_co', covariant=True)

logger = get_logger(__name__)


class PredictionDataset(Dataset[T_co]):
    """Dataset file so that score.py can process images in batches.

    """

    def __init__(self, root_dir: Optional[str] = None,
                 image_list_file: Optional[str] = None,
                 transforms: Optional[Compose] = None,
                 ignore_data_errors: bool = True,
                 input_dataset_id: Optional[str] = None,
                 ws: Optional[Workspace] = None,
                 datasetclass: Any = AmlDataset,
                 tile_grid_size: Optional[Tuple[int, int]] = None,
                 tile_overlap_ratio: Optional[float] = None):
        """
        :param root_dir: prefix to be added to the paths contained in image_list_file
        :type root_dir: str
        :param image_list_file: path to file containing list of images
        :type image_list_file: str
        :param transforms: function that takes in a pillow image and can generate tensor
        :type transforms: function
        :param ignore_data_errors: boolean flag on whether to ignore input data errors
        :type ignore_data_errors: bool
        :param input_dataset_id: The input dataset id.  If this is specified image_list_file is not required.
        :type input_dataset_id: str
        :param ws: The Azure ML Workspace
        :type ws: Workspace
        :param datasetclass: The Azure ML Dataset class
        :type datasetclass: Dataset
        :param tile_grid_size: The grid size to split the image into, if tiling is enabled. None, otherwise
        :type tile_grid_size: Tuple[int, int]
        :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
                                   None, if tile_grid_size is None
        :type tile_overlap_ratio: float
        """
        self._elements = []

        validate_tiling_settings(tile_grid_size, tile_overlap_ratio)

        self._tile_grid_size = tile_grid_size
        self._tile_overlap_ratio = tile_overlap_ratio
        self._ignore_data_errors = ignore_data_errors
        self._transform = transforms

        if input_dataset_id is not None:
            dataset_helper = AmlDatasetHelper(input_dataset_id, ws, ignore_data_errors,
                                              image_column_name=AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME,
                                              datasetclass=datasetclass)
            files = dataset_helper.get_file_name_list()
            self._elements = [TilingDatasetElement(f.strip("/"), None) for f in files]
            self._root_dir = dataset_helper._data_dir
        else:
            files = self._get_files_from_image_list_file(root_dir, image_list_file, ignore_data_errors)
            self._elements = [TilingDatasetElement(f, None) for f in files]
            self._root_dir = cast(str, root_dir)

        # Add tile elements
        if self._tile_grid_size is not None:
            logger.info("Size of dataset before adding tiles: {}".format(len(self._elements)))
            self._add_tile_elements()

        # Length of final dataset
        logger.info("Size of dataset: {}".format(len(self._elements)))

    def __len__(self) -> int:
        """Size of the dataset."""
        return len(self._elements)

    @staticmethod
    def collate_function(batch: Iterable[Any]) -> Tuple[Any, ...]:
        """Collate function for the dataset"""
        return tuple(zip(*batch))

    def __getitem__(self, idx: int) -> Tuple[str, Optional[Tensor], Optional[Dict[str, Any]]]:
        """
        :param idx: index
        :type idx: int
        :return: filename, image and image info at index idx
        :rtype: tuple[str, image, image_info]
        """
        filename, full_path = self.get_image_full_path(idx)
        tile = self._elements[idx].tile

        image = _read_image(self._ignore_data_errors, full_path, tile=tile)
        if image is None:
            return filename, None, None

        width, height = image.width, image.height
        if image is not None:
            if self._transform:
                image = self._transform(image)

        image_info = {"original_width": width, "original_height": height}
        if tile is not None:
            # torch.utils.data.dataloader.default_collate function throws a TypeError when any of the
            # fields in the item returned by the dataset has None values.
            # So, adding the tile field here only if it is not None.
            image_info.update({"tile": tile})
        return filename, image, image_info

    def get_image_full_path(self, idx: int) -> Tuple[str, str]:
        """Returns the filename and full file path for the given index.

        :param idx: index of the file to return
        :type idx: int
        :return: a tuple filename, full file path
        :rtype: tuple
        """
        filename = self._elements[idx].image_url
        if self._root_dir and filename:
            filename = filename.lstrip("/")
        full_path = os.path.join(self._root_dir, filename)
        return filename, full_path

    def _add_tile_elements(self) -> None:
        """Add image tiles generated using self._tile_grid_size to self._elements."""
        if self._tile_grid_size is None or self._tile_overlap_ratio is None:
            logger.warning("tile_grid_size or tile_overlap_ratio is None. Cannot add tile elements.")
            return

        tiling_start = time.time()
        logger.info("Adding tiles generated using grid size {} and overlap ratio {} to the dataset."
                    .format(self._tile_grid_size, self._tile_overlap_ratio))
        tile_elements = []

        for index, entry in enumerate(self._elements):
            _, full_path = self.get_image_full_path(index)
            image_size = _read_image_dimensions(self._ignore_data_errors, full_path)

            if image_size is not None:
                tiles = get_tiles(self._tile_grid_size, self._tile_overlap_ratio, image_size)
                tile_elements.extend([TilingDatasetElement(entry.image_url, tile) for tile in tiles])

        logger.info("Generated {} tiles in {} sec".format(len(tile_elements), time.time() - tiling_start))

        self._elements.extend(tile_elements)

    def _get_files_from_image_list_file(self, root_dir: Optional[str], image_list_file: Any,
                                        ignore_data_errors: bool = True) -> List[str]:
        files = []
        with open(image_list_file) as fp:
            lines = fp.readlines()
            parse_as_json_file = True
            if len(lines) > 0:
                try:
                    json.loads(lines[0])
                    logger.info("Parsing image list file as a JSON file")
                except json.JSONDecodeError:
                    parse_as_json_file = False

            if parse_as_json_file:
                files = self._parse_image_file_as_json(root_dir, lines, ignore_data_errors)
            else:
                for row in lines:
                    # filter out label info if present
                    file_data = row.split('\t')
                    filename = file_data[0].strip()
                    if not filename:
                        if not ignore_data_errors:
                            raise AutoMLVisionDataException('Input image file contains empty row', has_pii=False)
                        continue
                    full_path = os.path.join(root_dir, filename) if root_dir is not None else filename
                    if _validate_image_exists(full_path, ignore_data_errors):
                        files.append(filename)

        return files

    def _parse_image_file_as_json(self, root_dir: Optional[str], lines: List[str],
                                  ignore_data_errors: bool) -> List[str]:
        files = []
        for row in lines:
            try:
                annotation = json.loads(row)
                if DatasetFieldLabels.IMAGE_URL not in annotation:
                    missing_required_fields_message = "Missing required fields in annotation"
                    if not ignore_data_errors:
                        raise AutoMLVisionDataException(missing_required_fields_message, has_pii=False)
                    continue
                filename = annotation[DatasetFieldLabels.IMAGE_URL]
                filename = filename.strip()
                full_path = os.path.join(root_dir, filename) if root_dir is not None else filename
                if _validate_image_exists(full_path, ignore_data_errors):
                    files.append(filename)
            except json.JSONDecodeError:
                if not ignore_data_errors:
                    raise AutoMLVisionDataException("Invalid JSON object detected in file", has_pii=False)
                continue
        return files
