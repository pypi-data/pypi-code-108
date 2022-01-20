import os

from scene_engine.rest.helpers.annotations import coco_annotation
from shapely.geometry import Polygon
from shared.coordinate_interaction_enricher.enricher import (
    coordinate_interaction_enricher, create_polygon_list)
from shared.external.constants import AnnotationTypes
from shared.external.custom_exceptions import InvalidAnnotationError
from shared.external.models.annotation import AnnotationEntity
from shared.external.models.annotation_transformers.scale import \
    ScaleAnnotation
from shared.external.tools.logger import get_logger
from shared.tools.misc import json_file_to_dic

logger = get_logger(__name__)

my_path = path = os.path.dirname(os.path.abspath(__file__))


class TestCoco:
    def test_coco(self):
        """Simple unit test to test the coco annotation generator."""

        annotation_metadata = [
            {
                "id": "ooc_1.000.0000000003-cor.ann",
                "session_name": "ooc_1",
                "timestamp": "2020-07-31T19:13:31.004260+00:00",
                "asset_id": "ooc_1.000.0000000003-cor.png",
                "media_type": "images",
                "provider": "rendered",
                "annotation_type": "two_d_bounding_box",
                "annotation_entities": [],
                "sets": ["2ef58f20-cd29-437d-aac5-b71f2d267431"],
                "binary_id": None,
                "labels": [],
            },
            {
                "id": "ooc_1.000.0000000010-cor.ann",
                "session_name": "ooc_1",
                "timestamp": "2020-07-31T19:14:06.435951+00:00",
                "asset_id": "ooc_1.000.0000000010-cor.png",
                "media_type": "images",
                "provider": "rendered",
                "annotation_type": "two_d_bounding_box",
                "annotation_entities": [
                    {
                        "uid": "ec868ba6f16a8a2b4a5622af2b76c733",
                        "label": "car",
                        "annotation_type": "two_d_bounding_box",
                        "attributes": None,
                        "url": None,
                        "resource": None,
                        "coordinates": [
                            {"x": 167.5, "y": 121.5},
                            {"x": 194.5, "y": 121.5},
                            {"x": 194.5, "y": 157.5},
                            {"x": 167.5, "y": 157.5},
                        ],
                        "related_annotations": [],
                        "binary_id": None,
                        "category_id": 1,
                    }
                ],
                "sets": ["2ef58f20-cd29-437d-aac5-b71f2d267431"],
                "binary_id": None,
                "labels": ["car"],
            },
        ]
        images_metadata = [
            {
                "session_name": "ooc_1",
                "timestamp": "2020-03-20T19:00:00+00:00",
                "filename": "ooc_1.000.0000000003-cor.png",
                "sets": ["67eb75f4-9d5a-45f5-b555-d8ef231007b4"],
                "width": 256,
                "height": 256,
                "background": "travis_afb_001",
                "thumbnails": {
                    "tiny": {
                        "resolution": {"height": 100, "width": 100},
                        "filename": "ooc_1_tiny.000.0000000003-cor.png"
                    },
                    "small": {
                        "resolution": {"height": 300, "width": 300},
                        "filename": "ooc_1_small.000.0000000003-cor.png"
                    }
                }
            },
            {
                "session_name": "ooc_1",
                "timestamp": "2020-03-20T19:00:00+00:00",
                "filename": "ooc_1.000.0000000010-cor.png",
                "sets": ["67eb75f4-9d5a-45f5-b555-d8ef231007b4"],
                "width": 256,
                "height": 256,
                "background": "travis_afb_001",
                "thumbnails": {
                    "tiny": {
                        "resolution": {"height": 100, "width": 100},
                        "filename": "ooc_1_tiny.000.0000000010-cor.png"
                    },
                    "small": {
                        "resolution": {"height": 300, "width": 300},
                        "filename": "ooc_1_small.000.0000000010-cor.png"
                    }
                }
            }
        ]
        timestamp = "2020-04-04"
        year = "2020"
        description = "Mock annotation set"
        res = coco_annotation(
            annotation_metadata, images_metadata, timestamp, year, description
        )
        expected_res = {
            "info": {
                "description": "Mock annotation set",
                "url": "",
                "version": "",
                "year": "2020",
                "contributor": "",
                "date_created": "2020-04-04",
            },
            "licenses": [],
            "images": [
                {
                    "license": "",
                    "file_name": "ooc_1.000.0000000003-cor.png",
                    "coco_url": "",
                    "height": 256,
                    "width": 256,
                    "date_captured": "2020-03-20T19:00:00+00:00",
                    "flickr_url": "",
                    "id": 0,
                },
                {
                    "license": "",
                    "file_name": "ooc_1.000.0000000010-cor.png",
                    "coco_url": "",
                    "height": 256,
                    "width": 256,
                    "date_captured": "2020-03-20T19:00:00+00:00",
                    "flickr_url": "",
                    "id": 1,
                },
            ],
            "annotations": [
                {
                    "iscrowd": 0,
                    "image_id": 1,
                    "id": 0,
                    "category_id": 1,
                    "bbox": [167.5, 121.5, 27.0, 36.0],
                }
            ],
            "categories": [{"supercategory": "", "name": "car", "id": 1}],
        }

        assert res == expected_res


class TestAnnotationEntity:
    def test_creation(self):
        coordinates = [{'x': 448.0, 'y': 467.0},
                       {'x': 485.0, 'y': 467.0},
                       {'x': 485.0, 'y': 487.0},
                       {'x': 448.0, 'y': 487.0}]
        confidence = 0.75
        annotation_entity = AnnotationEntity(
            label="car",
            annotation_type=AnnotationTypes.TWO_D_BOUNDING_BOX,
            coordinates=coordinates,
            confidence=confidence
        )
        assert annotation_entity.label == "car"
        assert annotation_entity.confidence == 0.75

    def test_error_at_creation(self):
        try:
            coordinates = [{'x': 448.0, 'y': 467.0},
                           {'x': 485.0, 'y': 467.0},
                           {'x': 485.0, 'y': 487.0},
                           {'x': 448.0, 'y': 487.0}]
            confidence = 1
            annotation_entity = AnnotationEntity(
                label="car",
                annotation_type=AnnotationTypes.TWO_D_BOUNDING_BOX,
                coordinates=coordinates,
                confidence=confidence
            )
        except InvalidAnnotationError as e:
            assert "invalid confidence format <class 'int'>" == e.__str__()


class TestAnnotationCoordinateInteraction:
    def test_polygon_creation(self):
        coordinates = [{'x': 448.0, 'y': 467.0},
                       {'x': 485.0, 'y': 467.0},
                       {'x': 485.0, 'y': 487.0},
                       {'x': 448.0, 'y': 487.0}]
        confidence = 0.75
        annotation_entities = [
            {
                "label": 'car',
                "annotation_type": AnnotationTypes.TWO_D_BOUNDING_BOX,
                "coordinates": coordinates,
                "confidence": confidence
            },
            {
                "label": 'car',
                "annotation_type": AnnotationTypes.TWO_D_BOUNDING_BOX,
                "coordinates": coordinates,
                "confidence": confidence
            }]
        polygons = create_polygon_list(
            entities=annotation_entities, label="car")
        assert len(polygons) == 2
        assert isinstance(polygons[0], Polygon)
        assert isinstance(polygons[1], Polygon)

    def test_annotation_coordinate_interaction(self):
        annotation_with_collision = ScaleAnnotation(json_file_to_dic(
            os.path.join(my_path, 'resources/annotation_interaction_with_collision.ann')))
        annotation_without_collision = ScaleAnnotation(json_file_to_dic(os.path.join(
            my_path, 'resources/annotation_interaction_without_collision.ann')))

        # 3 annotations entities, 2 trucks and 1 car.
        annotation_with_collision_dict = annotation_with_collision.to_dic()
        annotation_without_collision_dict = annotation_without_collision.to_dic()
        time_tolerance = 1
        assert (
            coordinate_interaction_enricher(
                annotation_meta=annotation_with_collision_dict,
                labels=[
                    "truck",
                    "car"])) == [
            annotation_with_collision.timestamp,
            annotation_with_collision.timestamp]
        assert (coordinate_interaction_enricher
                (annotation_meta=annotation_without_collision_dict,
                 labels=["truck", "car"])) == []
        #  Checks if two trucks are colliding which they are not
        #  with the given coordinates although car and truck still collide
        assert (coordinate_interaction_enricher
                (annotation_meta=annotation_with_collision_dict,
                 labels=["truck", "truck"])) == []
        # Checks if two cars are colliding but there is only one car in the
        # annotation
        assert (coordinate_interaction_enricher
                (annotation_meta=annotation_with_collision_dict,
                 labels=["car", "car"])) == []

    def test_annotation_coordinate_interaction_static_mask(self):
        annotation_with_collision = ScaleAnnotation(json_file_to_dic(
            os.path.join(my_path, 'resources/annotation_interaction_with_collision.ann')))

        static_masks = [{"label": "test_mask_1",
                         "coordinates": [{'x': 40.0, 'y': 25.0},
                                         {'x': 40.0, 'y': 10.0},
                                         {'x': 50.0, 'y': 10.0},
                                         {'x': 50.0, 'y': 25.0}]},
                        {"label": "test_mask_2",
                         "coordinates": [{'x': 30.0, 'y': 25.0},
                                         {'x': 30.0, 'y': 10.0},
                                         {'x': 40.0, 'y': 10.0},
                                         {'x': 40.0, 'y': 25.0}]},
                        {"label": "test_mask_3",
                         "coordinates": [{'x': 100.0, 'y': 25.0},
                                         {'x': 100.0, 'y': 10.0},
                                         {'x': 120.0, 'y': 10.0},
                                         {'x': 120.0, 'y': 25.0}]}]

        annotation_with_collision_dict = annotation_with_collision.to_dic()
        time_tolerance = 1
        assert (coordinate_interaction_enricher
                (annotation_meta=annotation_with_collision_dict,
                 labels=["test_mask_1", "car"],
                 static_masks=static_masks)) == []
        assert (coordinate_interaction_enricher
                (annotation_meta=annotation_with_collision_dict,
                 labels=["test_mask_3", "car"],
                 static_masks=static_masks)) == []
        assert (coordinate_interaction_enricher
                (annotation_meta=annotation_with_collision_dict,
                 labels=["test_mask_1", "truck"],
                 static_masks=static_masks)) == [annotation_with_collision.timestamp,
                                                 annotation_with_collision.timestamp]
