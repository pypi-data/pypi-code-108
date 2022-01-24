import pytest
import torch

from azureml.automl.dnn.vision.common.average_meter import AverageMeter
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException
from azureml.automl.dnn.vision.common.tiling_dataset_element import Tile
from azureml.automl.dnn.vision.common.tiling_utils import get_tiles
from azureml.automl.dnn.vision.object_detection.common.constants import DatasetFieldLabels
from azureml.automl.dnn.vision.object_detection.common.tiling_helper import generate_tiles_annotations, \
    convert_tile_boxes_to_image_dimensions, get_duplicate_box_indices, \
    merge_predictions_from_tiles_and_images_single_image, merge_predictions_from_tiles_and_images
from azureml.automl.dnn.vision.object_detection.data.object_annotation import ObjectAnnotation


class TestTilingHelper:

    def _get_normalized_xyxy(self, x, y, w, h, image_size):
        return x / image_size[0], y / image_size[1], (x + w) / image_size[0], (y + h) / image_size[1]

    def _create_object_annotation(self, x0, y0, x1, y1, label, iscrowd):
        return ObjectAnnotation({
            DatasetFieldLabels.CLASS_LABEL: label,
            DatasetFieldLabels.X_0_PERCENT: x0,
            DatasetFieldLabels.Y_0_PERCENT: y0,
            DatasetFieldLabels.X_1_PERCENT: x1,
            DatasetFieldLabels.Y_1_PERCENT: y1,
            DatasetFieldLabels.IS_CROWD: iscrowd
        })

    def test_generate_tiles_annotations_annotation_in_some_tiles(self):
        image_size = (640, 480)
        tile_grid_size = [3, 2]
        tile_overlap_ratio = 0.25

        # Object overlapping only the first tile
        x0, y0, x1, y1 = self._get_normalized_xyxy(0, 0, 20, 200, image_size)
        annotation = self._create_object_annotation(x0, y0, x1, y1, "label", 0)
        tile_annotations = generate_tiles_annotations([annotation], tile_grid_size, tile_overlap_ratio, image_size)
        for index, value in enumerate(tile_annotations.values()):
            if index == 0:
                assert len(value) == 1
            else:
                assert len(value) == 0

    def test_generate_tiles_annotations_annotations_on_tile_boundary(self):
        image_size = (640, 480)
        tile_grid_size = [3, 2]
        tile_overlap_ratio = 0.25

        # Object annotation falling on tile boundary along x-axis between tile 0 and tile 2.
        x0, y0, x1, y1 = self._get_normalized_xyxy(0, 100, 192, 100, image_size)
        annotation = self._create_object_annotation(x0, y0, x1, y1, "label", 0)
        tile_annotations = generate_tiles_annotations([annotation], tile_grid_size, tile_overlap_ratio, image_size)
        assert len(tile_annotations) == 6
        for index, value in enumerate(tile_annotations.values()):
            # Annotation should be part of tile 0 and not part of tile 2.
            if index == 0:
                assert len(value) == 1
            elif index == 2:
                assert len(value) == 0

    def test_generate_tiles_annotations_zero_width(self):
        image_size = (640, 480)
        tile_grid_size = [2, 1]
        tile_overlap_ratio = 0.0

        # Annotation boxes in xyxy format
        annotation_boxes = [
            # Valid boxes for tile 0 and
            [0, 100, 319, 200],  # invalid box for tile 1: x1 (320) > x2 (319) and int(x1) > int(x2)
            [0, 100, 319.3, 200],  # invalid box for tile 1: x1 (320) > x2 (319.3) and int(x1) > int(x2)
            [0, 100, 320, 200],  # invalid box for tile 1: x1 (320) = x2 (320) and int(x1) = int(x2)
            [0, 100, 320.7, 200],  # invalid box for tile 1: x1 (320) < x2 (320.7) and int(x1) = int(x2)
            [0, 100, 321, 200],  # valid box for tile 1: x1 (320) < x2 (321) and int(x1) < int(x2)
            # Valid boxes for tile 1 and
            [319, 100, 400, 200],  # valid box for tile 0: x1 (319) < x2 (320) and int(x1) < int(x2)
            [319.3, 100, 400, 200],  # valid box for tile 0: x1 (319.3) < x2 (320) and int(x1) < int(x2)
            [320, 100, 400, 200],  # invalid box for tile 0: x1 (320) = x2 (320) and int(x1) = int(x2)
            [320.7, 100, 400, 200],  # invalid box for tile 0: x1 (320.7) > x2 (320) and int(x1) = int(x2)
            [321, 100, 400, 200],  # invalid box for tile 0: x1 (321) > x2 (320) and int(x1) > int(x2)
        ]

        annotation_normalized_boxes = [self._get_normalized_xyxy(box[0], box[1], box[2], box[3], image_size)
                                       for box in annotation_boxes]
        annotations = [self._create_object_annotation(box[0], box[1], box[2], box[3], "label", 0)
                       for box in annotation_normalized_boxes]
        tile_annotations = generate_tiles_annotations(annotations, tile_grid_size, tile_overlap_ratio, image_size)
        assert len(tile_annotations) == 2
        for index, value in enumerate(tile_annotations.values()):
            if index == 0:
                assert len(value) == 7
            else:
                assert len(value) == 6

    def test_generate_tiles_annotations(self):

        def _test(image_size, tile_grid_size, tile_overlap_ratio):
            tiles = get_tiles(tile_grid_size, tile_overlap_ratio, image_size)

            image_annotations = []
            expected_tile_annotations = {tile: [] for tile in tiles}
            for index, tile in enumerate(tiles):
                tile_width = tile.bottom_right_x - tile.top_left_x
                tile_height = tile.bottom_right_y - tile.top_left_y
                is_last_tile_x_axis = tile.bottom_right_x == image_size[0]
                is_last_tile_y_axis = tile.bottom_right_y == image_size[1]
                next_tile_x_axis_index = None if is_last_tile_x_axis else index + tile_grid_size[1]
                next_tile_y_axis_index = None if is_last_tile_y_axis else index + 1

                # Annotation that only in one tile.
                x0, y0, x1, y1 = self._get_normalized_xyxy(tile.top_left_x + 0.3 * tile_width,
                                                           tile.top_left_y + 0.3 * tile_height,
                                                           0.4 * tile_width, 0.4 * tile_height,
                                                           image_size)
                image_annotations.append(self._create_object_annotation(x0, y0, x1, y1, "label1", 0))
                expected_tile_annotations[tiles[index]].append(
                    self._create_object_annotation(0.3, 0.3, 0.7, 0.7, "label1", 0))

                if not is_last_tile_x_axis:
                    # Annotation that intersects with next tile in x-axis.
                    x0, y0, x1, y1 = self._get_normalized_xyxy(tile.top_left_x + 0.8 * tile_width,
                                                               tile.top_left_y + 0.3 * tile_height,
                                                               0.4 * tile_width, 0.4 * tile_height,
                                                               image_size)
                    image_annotations.append(self._create_object_annotation(x0, y0, x1, y1, "label2", 1))
                    expected_tile_annotations[tiles[index]].append(
                        self._create_object_annotation(0.8, 0.3, 1.0, 0.7, "label2", 1))
                    expected_tile_annotations[tiles[next_tile_x_axis_index]].append(
                        self._create_object_annotation(0.05, 0.3, 0.45, 0.7, "label2", 1))

                if not is_last_tile_y_axis:
                    # Annotation that intersects with next tile in y-axis.
                    x0, y0, x1, y1 = self._get_normalized_xyxy(tile.top_left_x + 0.3 * tile_width,
                                                               tile.top_left_y + 0.8 * tile_height,
                                                               0.4 * tile_width, 0.4 * tile_height,
                                                               image_size)
                    image_annotations.append(self._create_object_annotation(x0, y0, x1, y1, "label3", 0))
                    expected_tile_annotations[tiles[index]].append(
                        self._create_object_annotation(0.3, 0.8, 0.7, 1.0, "label3", 0))
                    expected_tile_annotations[tiles[next_tile_y_axis_index]].append(
                        self._create_object_annotation(0.3, 0.05, 0.7, 0.45, "label3", 0))

                if not is_last_tile_x_axis and not is_last_tile_y_axis:
                    # Annotation that intersects with next tiles in both x and y axes.
                    x0, y0, x1, y1 = self._get_normalized_xyxy(tile.top_left_x + 0.8 * tile_width,
                                                               tile.top_left_y + 0.8 * tile_height,
                                                               0.4 * tile_width, 0.4 * tile_height,
                                                               image_size)
                    image_annotations.append(self._create_object_annotation(x0, y0, x1, y1, "label4", 1))
                    expected_tile_annotations[tiles[index]].append(
                        self._create_object_annotation(0.8, 0.8, 1.0, 1.0, "label4", 1))
                    expected_tile_annotations[tiles[next_tile_x_axis_index]].append(
                        self._create_object_annotation(0.05, 0.8, 0.45, 1.0, "label4", 1))
                    expected_tile_annotations[tiles[next_tile_y_axis_index]].append(
                        self._create_object_annotation(0.8, 0.05, 1.0, 0.45, "label4", 1))

                    next_tile_x_y_index = index + tile_grid_size[1] + 1
                    expected_tile_annotations[tiles[next_tile_x_y_index]].append(
                        self._create_object_annotation(0.05, 0.05, 0.45, 0.45, "label4", 1))

            tile_annotations = generate_tiles_annotations(image_annotations, tile_grid_size, tile_overlap_ratio,
                                                          image_size)
            for tile, annotations in tile_annotations.items():
                expected_annotations = expected_tile_annotations[tile]
                assert len(annotations) == len(expected_annotations)
                for i, annotation in enumerate(annotations):
                    assert annotation[DatasetFieldLabels.CLASS_LABEL] == expected_annotations[i].label
                    assert annotation[DatasetFieldLabels.IS_CROWD] == expected_annotations[i].iscrowd
                    annotation_box = torch.tensor([annotation[DatasetFieldLabels.X_0_PERCENT],
                                                   annotation[DatasetFieldLabels.Y_0_PERCENT],
                                                   annotation[DatasetFieldLabels.X_1_PERCENT],
                                                   annotation[DatasetFieldLabels.Y_1_PERCENT]])
                    expected_annotation_box = torch.tensor([expected_annotations[i]._x0_percentage,
                                                            expected_annotations[i]._y0_percentage,
                                                            expected_annotations[i]._x1_percentage,
                                                            expected_annotations[i]._y1_percentage])
                    torch.testing.assert_allclose(annotation_box, expected_annotation_box, rtol=1e-03, atol=1e-02)

        image_sizes = [(640, 480), (1080, 1080), (1280, 720), (1920, 1080)]
        tile_grid_sizes = [(2, 1), (1, 2), (3, 2), (2, 3), (4, 3), (3, 4)]
        tile_overlap_ratio = 0.25
        for image_size in image_sizes:
            for tile_grid_size in tile_grid_sizes:
                _test(image_size, tile_grid_size, tile_overlap_ratio)

    def test_convert_tile_boxes_to_image_dimensions(self):
        original_image_size = (640, 480)
        # image_size_ratio correspond to ratio in which image is scaled after applying transforms
        image_size_ratios = [0.7, 1, 1.3]

        for image_size_ratio in image_size_ratios:
            image_size = (int(original_image_size[0] * image_size_ratio),
                          int(original_image_size[1] * image_size_ratio))

            original_tiles = [(0, 0, 300, 200), (100, 100, 400, 300), (340, 280, 640, 480)]
            # tile_size_ratio correspond to ratio in which tile is scaled after applying transforms
            tile_size_ratios = [0.7, 1, 1.3]

            for original_tile in original_tiles:
                for tile_size_ratio in tile_size_ratios:
                    original_tile_size = (original_tile[2] - original_tile[0], original_tile[3] - original_tile[1])
                    tile_size = (int(original_tile_size[0] * tile_size_ratio),
                                 int(original_tile_size[1] * tile_size_ratio))
                    # Tile bounding boxes relative to tile dimensions after applying transforms
                    boxes = torch.tensor(
                        [[0, 0, tile_size[0] / 2, tile_size[1] / 2],  # top-left
                         [tile_size[0] / 2, tile_size[1] / 2, tile_size[0], tile_size[1]]],  # bottom-right
                        dtype=torch.float)

                    # Expected boxes relative to image dimensions after applying transforms
                    expected_boxes = boxes.clone()
                    expected_boxes[:, 0] = ((expected_boxes[:, 0] / tile_size_ratio) + original_tile[0]) * \
                        image_size_ratio
                    expected_boxes[:, 1] = ((expected_boxes[:, 1] / tile_size_ratio) + original_tile[1]) * \
                        image_size_ratio
                    expected_boxes[:, 2] = ((expected_boxes[:, 2] / tile_size_ratio) + original_tile[0]) * \
                        image_size_ratio
                    expected_boxes[:, 3] = ((expected_boxes[:, 3] / tile_size_ratio) + original_tile[1]) * \
                        image_size_ratio

                    convert_tile_boxes_to_image_dimensions(boxes, Tile(original_tile), tile_size, original_tile_size,
                                                           image_size, original_image_size, "cpu")

                    assert torch.allclose(boxes, expected_boxes)

    def test_get_duplicate_box_indices(self):

        def _test(boxes, scores, labels, tiles):
            bounding_boxes = torch.tensor(boxes, dtype=torch.float)
            bounding_box_scores = torch.tensor(scores, dtype=torch.float)
            bounding_box_labels = torch.tensor(labels, dtype=torch.int64)
            bounding_box_tiles = torch.tensor(tiles, dtype=torch.float)

            duplicate_indices = get_duplicate_box_indices(bounding_boxes, bounding_box_scores,
                                                          bounding_box_labels, bounding_box_tiles, 0.25, "cpu")
            assert duplicate_indices.numel() == len(boxes)
            return duplicate_indices

        image = [0, 0, 600, 400]
        tiles = [(0, 0, 400, 300), (0, 100, 400, 400),
                 (200, 0, 600, 300), (200, 100, 600, 400)]

        result_dtype = torch.uint8
        # No boxes
        duplicate_indices = _test([], [], [], [])
        assert torch.equal(duplicate_indices, torch.tensor([], dtype=result_dtype))

        # Boxes from different label should not be considered for duplicate detection
        duplicate_indices = _test([[0, 100, 100, 200], [0, 100, 100, 200]],
                                  [0.9, 0.8], [1, 2], [tiles[0], tiles[1]])
        assert torch.count_nonzero(duplicate_indices) == 0

        # Boxes from same tile should not be considered for duplicate detection
        duplicate_indices = _test([[0, 100, 100, 200], [0, 100, 100, 200]],
                                  [0.9, 0.8], [1, 1], [tiles[0], tiles[0]])
        assert torch.count_nonzero(duplicate_indices) == 0

        # Boxes with iou < iou_threshold
        duplicate_indices = _test([[0, 100, 100, 200], [0, 175, 100, 275]],
                                  [0.9, 0.8], [1, 1], [tiles[0], tiles[1]])
        assert torch.count_nonzero(duplicate_indices) == 0

        # Boxes from different tiles
        duplicate_indices = _test([[0, 100, 100, 200], [0, 100, 100, 200]],
                                  [0.9, 0.8], [1, 1], [tiles[0], tiles[1]])
        assert torch.equal(duplicate_indices, torch.tensor([0, 1], dtype=result_dtype))

        # Boxes with lower score are considered as duplicates
        duplicate_indices = _test([[0, 100, 100, 200], [0, 100, 100, 200]],
                                  [0.8, 0.9], [1, 1], [tiles[0], tiles[1]])
        assert torch.equal(duplicate_indices, torch.tensor([1, 0], dtype=result_dtype))

        # Boxes from tile and image
        duplicate_indices = _test([[0, 100, 100, 200], [0, 100, 100, 200]],
                                  [0.9, 0.8], [1, 1], [tiles[0], image])
        assert torch.equal(duplicate_indices, torch.tensor([0, 1], dtype=result_dtype))

        # Object completely in tile[0] and partially in tile[1]
        duplicate_indices = _test([[0, 90, 100, 190], [0, 100, 100, 190]],
                                  [0.9, 0.8], [1, 1], [tiles[0], tiles[1]])
        assert torch.equal(duplicate_indices, torch.tensor([0, 1], dtype=result_dtype))

        # Two small boxes in a tile, overlapping with a bigger box from image
        # with box from image having lower score
        duplicate_indices = _test([[0, 100, 50, 200], [50, 100, 100, 200], [0, 100, 100, 200]],
                                  [0.9, 0.9, 0.8], [1, 1, 1], [tiles[0], tiles[0], image])
        assert torch.equal(duplicate_indices, torch.tensor([0, 0, 1], dtype=result_dtype))

        # Two small boxes in a tile, overlapping with a bigger box from image
        # with box from image having higher score
        duplicate_indices = _test([[0, 100, 50, 200], [50, 100, 100, 200], [0, 100, 100, 200]],
                                  [0.7, 0.8, 0.9], [1, 1, 1], [tiles[0], tiles[0], image])
        assert torch.equal(duplicate_indices, torch.tensor([1, 1, 0], dtype=result_dtype))

        # Multiple overlapping and non-overlapping boxes from different tiles.
        # Overlapping boxes slightly differ from each other
        boxes = [[50, 25, 150, 75],  # box from tile[0]
                 [50, 175, 150, 225], [50, 180, 150, 230],  # box overlapping tile[0] and tile[1]
                 [50, 325, 150, 375],  # box from tile[1]
                 [250, 25, 350, 75], [255, 25, 355, 75],  # box overlapping tile[0] and tile[2]
                 # box overlapping all 4 tiles
                 [250, 175, 350, 225], [250, 180, 350, 230], [255, 175, 355, 225], [255, 180, 355, 230],
                 [250, 325, 350, 375], [255, 325, 355, 375],  # box overlapping tile[1] and tile[3]
                 [450, 25, 550, 75],  # box from tile[2]
                 [450, 175, 550, 225], [450, 180, 550, 230],  # box from tile[2] and tile[3]
                 [450, 325, 550, 375]]  # box from tile[3]
        box_tiles = [tiles[0],
                     tiles[0], tiles[1],
                     tiles[1],
                     tiles[0], tiles[2],
                     tiles[0], tiles[1], tiles[2], tiles[3],
                     tiles[1], tiles[3],
                     tiles[2],
                     tiles[2], tiles[3],
                     tiles[3]]
        box_scores = [0.9,
                      0.8, 0.9,
                      0.9,
                      0.9, 0.8,
                      0.6, 0.8, 0.9, 0.7,
                      0.8, 0.7,
                      0.6,
                      0.6, 0.8,
                      0.9]
        expected_duplicates = torch.tensor([0,
                                            1, 0,
                                            0,
                                            0, 1,
                                            1, 1, 0, 1,
                                            0, 1,
                                            0,
                                            1, 0,
                                            0], dtype=result_dtype)
        duplicate_indices = _test(boxes, box_scores, [1] * len(boxes), box_tiles)
        assert torch.equal(duplicate_indices, expected_duplicates)

    @staticmethod
    def _create_label_with_info(boxes, labels, scores, image_url, tile, original_image_shape,
                                original_tile_shape, image_size_ratio, tile_size_ratio):
        original_width = original_tile_shape[0] if tile is not None else original_image_shape[0]
        original_height = original_tile_shape[1] if tile is not None else original_image_shape[1]
        label_with_info = {
            "boxes": torch.tensor(boxes, dtype=torch.float),
            "labels": torch.tensor(labels, dtype=torch.int64),
            "scores": torch.tensor(scores, dtype=torch.float),
            "width": original_width * (image_size_ratio if tile is None else tile_size_ratio),
            "height": original_height * (image_size_ratio if tile is None else tile_size_ratio),
            "original_width": original_width,
            "original_height": original_height,
            "filename": image_url
        }
        if tile is not None:
            label_with_info["tile"] = tile
        return label_with_info

    def test_merge_predictions_from_tiles_and_images_single_image(self):
        nms_time = AverageMeter()
        nms_threshold = 0.25

        original_image_shape = (600, 400)
        original_tile_shape = (300, 200)
        image_size_ratio = 1.5
        tile_size_ratio = 3

        sample_tile = Tile((0, 0, 300, 200))

        # No predictions from image should raise an error
        label_with_info_list = [self._create_label_with_info([], [], [], "1.jpg", sample_tile,
                                                             original_image_shape, original_tile_shape,
                                                             image_size_ratio, tile_size_ratio)]
        with pytest.raises(AutoMLVisionSystemException):
            merge_predictions_from_tiles_and_images_single_image(label_with_info_list, nms_threshold, nms_time, "cpu")

        label_with_info_list = [self._create_label_with_info([[0, 0, 100, 100]], [1], [0.9], "1.jpg", sample_tile,
                                                             original_image_shape, original_tile_shape,
                                                             image_size_ratio, tile_size_ratio),  # tile
                                self._create_label_with_info([[0, 0, 100, 100]], [2], [0.8], "1.jpg", None,
                                                             original_image_shape, original_tile_shape,
                                                             image_size_ratio, tile_size_ratio)  # image
                                ]
        merged_label_with_info = merge_predictions_from_tiles_and_images_single_image(
            label_with_info_list, nms_threshold, nms_time, "cpu")
        assert isinstance(merged_label_with_info, dict)
        for k, v in merged_label_with_info.items():
            if k not in ["boxes", "labels", "scores"]:
                # Other fields except boxes, labels and scores should have values from image_label_with_info
                assert v == label_with_info_list[1][k]
            else:
                # Should contain two boxes
                assert v.shape[0] == 2

        tile_box = [0, 0, 100, 100]
        tile_box_in_image_dimensions = [0, 0, (100 / tile_size_ratio) * image_size_ratio,
                                        (100 / tile_size_ratio) * image_size_ratio]
        # Duplicate boxe should be removed. In this example, the duplicate is from image.
        label_with_info_list = [self._create_label_with_info([tile_box], [1], [0.9], "1.jpg", sample_tile,
                                                             original_image_shape, original_tile_shape,
                                                             image_size_ratio, tile_size_ratio),  # tile
                                self._create_label_with_info([tile_box_in_image_dimensions], [1], [0.8], "1.jpg",
                                                             None, original_image_shape, original_tile_shape,
                                                             image_size_ratio, tile_size_ratio)  # image
                                ]
        merged_label_with_info = merge_predictions_from_tiles_and_images_single_image(
            label_with_info_list, nms_threshold, nms_time, "cpu")
        assert isinstance(merged_label_with_info, dict)
        # The result boxes should be in image dimensions
        assert torch.equal(merged_label_with_info["boxes"],
                           torch.tensor([tile_box_in_image_dimensions], dtype=torch.float))
        assert torch.equal(merged_label_with_info["labels"], torch.tensor([1], dtype=torch.int64))
        assert torch.equal(merged_label_with_info["scores"], torch.tensor([0.9], dtype=torch.float))

    def test_merge_predictions_from_tiles_and_images(self):
        original_image_shape = (600, 400)
        original_tile_shape = (300, 200)
        image_size_ratio = 1.5
        tile_size_ratio = 3
        merge_predictions_time = AverageMeter()
        nms_time = AverageMeter()

        sample_tile_1 = Tile((0, 0, 300, 200))
        sample_tile_2 = Tile((300, 0, 300, 200))
        tile_box = [0, 0, 100, 100]
        tile_1_box_in_image_dimensions = [0, 0, (100 / tile_size_ratio) * image_size_ratio,
                                          (100 / tile_size_ratio) * image_size_ratio]
        tile_2_box_in_image_dimensions = [300 * image_size_ratio, 0, (300 + 100 / tile_size_ratio) * image_size_ratio,
                                          (100 / tile_size_ratio) * image_size_ratio]
        label_with_info_list = [
            # For image 1, box from tile 1 is duplicate of box from image.
            self._create_label_with_info([tile_1_box_in_image_dimensions], [1], [0.9], "1.jpg", None,
                                         original_image_shape, original_tile_shape,
                                         image_size_ratio, tile_size_ratio),  # Image 1
            self._create_label_with_info([tile_box], [1], [0.8], "1.jpg", sample_tile_1,
                                         original_image_shape, original_tile_shape,
                                         image_size_ratio, tile_size_ratio),  # Image 1, tile 1
            self._create_label_with_info([tile_box], [1], [0.7], "1.jpg", sample_tile_2,
                                         original_image_shape, original_tile_shape,
                                         image_size_ratio, tile_size_ratio),  # Image 1, tile 2
            # For image 2, box from image is duplicate of box from tile 1.
            self._create_label_with_info([tile_1_box_in_image_dimensions], [1], [0.8], "2.jpg", None,
                                         original_image_shape, original_tile_shape,
                                         image_size_ratio, tile_size_ratio),  # Image 2
            self._create_label_with_info([tile_box], [1], [0.9], "2.jpg", sample_tile_1,
                                         original_image_shape, original_tile_shape,
                                         image_size_ratio, tile_size_ratio),  # Image 2, tile 1
            self._create_label_with_info([tile_box], [1], [0.7], "2.jpg", sample_tile_2,
                                         original_image_shape, original_tile_shape,
                                         image_size_ratio, tile_size_ratio),  # Image 2, tile 2
        ]

        merged_label_with_info_list = merge_predictions_from_tiles_and_images(label_with_info_list, 0.25, "cpu",
                                                                              merge_predictions_time,
                                                                              nms_time)
        # Only one result per image
        assert len(merged_label_with_info_list) == 2
        merged_label_with_info_list_sorted = sorted(merged_label_with_info_list, key=lambda x: x["filename"])

        for index, image_result in enumerate(merged_label_with_info_list_sorted):
            image_label_with_info = label_with_info_list[0] if index == 0 else label_with_info_list[3]
            expected_boxes = torch.tensor([tile_1_box_in_image_dimensions, tile_2_box_in_image_dimensions],
                                          dtype=torch.float)
            expected_labels = torch.tensor([1, 1], dtype=torch.int64)
            expected_scores = torch.tensor([0.9, 0.7], dtype=torch.float)
            for k, v in image_result.items():
                if k == "boxes":
                    assert torch.equal(v, expected_boxes)
                elif k == "labels":
                    assert torch.equal(v, expected_labels)
                elif k == "scores":
                    assert torch.equal(v, expected_scores)
                else:
                    # Other fields except boxes, labels and scores should have values from image_label_with_info
                    assert v == image_label_with_info[k]
