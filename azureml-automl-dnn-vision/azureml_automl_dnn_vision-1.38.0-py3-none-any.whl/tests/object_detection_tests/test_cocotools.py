import pytest
import torch

from azureml.automl.dnn.vision.object_detection.eval import cocotools
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import \
    CommonObjectDetectionDatasetWrapper, DatasetProcessingType

from ..common.run_mock import ObjectDetectionDatasetMock


class TestCocoTools:
    @pytest.mark.usefixtures("new_clean_dir")
    def test_match_with_first_gt(self):
        # Setup ground truth dataset
        dataset_items = [(None,
                          {"boxes": torch.tensor([[0, 0, 300, 200], [300, 200, 600, 400]], dtype=torch.float32),
                           "labels": torch.tensor([0, 0], dtype=torch.int64)},
                          {"areas": [60000, 60000], "iscrowd": [0, 0], "filename": "image_1.jpg",
                           "height": 400, "width": 600}
                          )]
        dataset = ObjectDetectionDatasetMock(dataset_items, 1)
        dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset, DatasetProcessingType.IMAGES)
        coco_index = cocotools.create_coco_index(dataset_wrapper)

        # Check that ground truths in coco_index don't have id 0.
        for ann in coco_index.dataset["annotations"]:
            assert ann["id"] != 0

        # Prediction that matches first ground truth.
        predictions = [{
            "image_id": "image_1.jpg", "bbox": [0, 0, 300, 200],
            "category_id": dataset.index_to_label(0), "score": 0.8
        }]

        coco_score = cocotools.score_from_index(coco_index, predictions)
        assert coco_score[0] > 0.0
