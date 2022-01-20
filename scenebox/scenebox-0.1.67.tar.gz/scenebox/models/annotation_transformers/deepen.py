#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

import json
import logging

from scene_engine.rest import ASSET_MANAGER_URL
from shared.external.clients.asset_manager_client import AssetManagerClient
from shared.external.constants import (AnnotationMediaTypes,
                                       AnnotationProviders, AnnotationTypes,
                                       AssetsConstants, AnnotationGroups)
from shared.external.custom_exceptions import InvalidAnnotationError
from shared.external.models.annotation import Annotation, AnnotationEntity
from shared.external.tools import time_utils

annotation_projects_asset_manager = AssetManagerClient(
    AssetsConstants.ANNOTATION_PROJECTS_ASSET_ID,
    metadata_only=True,
    asset_manager_url=ASSET_MANAGER_URL,
)


class DeepenAnnotation(Annotation):
    def __init__(
        self,
        annotation_project_id,
        file_id,
        file_labels,
        resolution=None,
        annotation_binary_id=None,
        version=None
    ):
        annotation_meta = annotation_projects_asset_manager.get_metadata(
            id=annotation_project_id
        )
        valid = False
        for set_id, set_files in json.loads(annotation_meta["state"]).items():
            if file_id in set_files:
                valid = True
                break
        if not valid:
            raise ValueError(
                "The file ID {} does not exist in the Annotation {}".format(
                    file_id, annotation_project_id
                )
            )
        self.file_id = file_id
        self.resolution = resolution
        self.annotation_meta = annotation_meta
        self.annotation_meta["binary_id"] = annotation_binary_id
        # Always only one set
        self.annotation_set_id = annotation_meta["sets"][0]
        self.file_labels = file_labels
        self.annotation_entities = []
        self._version = version
        self.timestamp = time_utils.string_to_datetime(
            self.annotation_meta.get("timestamp")
        )
        super().__init__(annotation_meta=annotation_meta)

    def set_id(self):
        self.id = self.annotation_meta["id"] + self.file_id + ".ann"

    def set_ground_truth(self):
        self.annotation_group = AnnotationGroups.GROUND_TRUTH

    def set_version(self):
        self.version = self._version

    def set_media_type(self):
        # TODO! FIXME! : Handle other annotation types?
        self.media_type = AssetsConstants.IMAGES_ASSET_ID

    def set_provider(self):
        self.provider = AnnotationProviders.DEEPEN

    def set_annotation_type(self):
        self.annotation_type = AnnotationTypes.TWO_D_BOUNDING_BOX

    def set_annotation_entities(self):
        # In general, there can be multiple types of labels for a single file
        # Never exit on error
        for deepen_label in self.file_labels:
            try:
                label_type = deepen_label["label_type"]
                if label_type == "box":
                    self.set_bounding_box_annotation_entities(deepen_label)
                elif label_type == "polygon":
                    self.set_polygon_annotation_entities(deepen_label)
            except Exception as e:
                logging.error(
                    "Could not set annotation entity::: {}".format(e))

    def set_set_membership(self):
        self.sets = [self.annotation_set_id]

    def set_bounding_box_annotation_entities(self, deepen_label):
        """
        Note: box is an array of 4 numbers representing a 2D bounding box. The first two numbers are the x, y
        coordinates of the top left corner of the box. 3rd and 4th numbers represent length of box
        along x and y axes. Coordinate system has origin at the top left corner of the image.
        """
        box = deepen_label["box"]
        try:
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            label = deepen_label["label_category_id"]
        except KeyError as e:
            raise InvalidAnnotationError(str(e))
        key = "{}_{}".format(deepen_label["file_id"], deepen_label["label_id"])
        coordinates = [
            {"x": left, "y": top},
            {"x": left + width, "y": top},
            {"x": left + width, "y": top + height},
            {"x": left, "y": top + height},
        ]
        self.annotation_entities.append(
            AnnotationEntity(
                label=label,
                annotation_type=AnnotationTypes.TWO_D_BOUNDING_BOX,
                coordinates=coordinates,
                attributes=deepen_label.get("attributes")
            )
        )

    def set_polygon_annotation_entities(self, deepen_label):
        """
        Note: Array of polygons. Each polygon is an array of points [x, y].
        """
        for polygon_part, polygon in enumerate(deepen_label["polygons"]):
            try:
                coordinates = [{"x": i[0], "y": i[1]} for i in polygon]
                key = "{}_{}_{}".format(
                    deepen_label["file_id"],
                    deepen_label["label_id"],
                    polygon_part)
                label = deepen_label["label_category_id"]
                coordinates.append(coordinates[0])
            except KeyError as e:
                raise InvalidAnnotationError(str(e))
            self.annotation_entities.append(
                AnnotationEntity(
                    label=label,
                    annotation_type=AnnotationTypes.POLYGON,
                    coordinates=coordinates,
                    attributes=deepen_label.get("attributes"),
                    uid=key
                )
            )
