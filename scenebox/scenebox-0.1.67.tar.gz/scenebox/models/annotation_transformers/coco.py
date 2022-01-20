#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#


from typing import List, Optional, Union

from shared.external.constants import AnnotationProviders, AnnotationTypes, AssetsConstants, AnnotationGroups
from shared.external.custom_exceptions import InvalidAnnotationError
from shared.external.models.annotation import Annotation, AnnotationEntity
from shared.external.tools import time_utils


class CocoAnnotation(Annotation):
    def __init__(
        self,
        image_dict: dict,
        annotations_dict: List[dict],
        categories_dict: List[dict],
        annotation_type: AnnotationTypes,
        set_name: Optional[str] = None,
        provider: Optional[Union[AnnotationProviders, str]] = None,
        version: Optional[str] = None,
        annotation_group=AnnotationGroups.GROUND_TRUTH
    ):
        metadata = {"image": image_dict, "categories": categories_dict}
        if annotation_type not in [
            AnnotationTypes.SEGMENTATION,
            AnnotationTypes.TWO_D_BOUNDING_BOX,
            AnnotationTypes.POLYGON,
        ]:
            raise InvalidAnnotationError(
                f"invalid annotation type {annotation_type}"
            )
        if "date_captured" in image_dict:
            timestamp = time_utils.string_to_datetime(
                image_dict["date_captured"]
            )
        else:
            timestamp = None

        asset_id = image_dict.get("file_name")

        super().__init__(
            annotation_meta=metadata,
            set_id=set_name,
            annotation_type=annotation_type,
            annotation_group=annotation_group,
            version=version,
            media_type=AssetsConstants.IMAGES_ASSET_ID,
            timestamp=timestamp,
            provider=provider,
            asset_id=asset_id,
            id=asset_id + "_" + provider
        )

        self.image_dict: dict = image_dict
        self.annotations_dict: List[dict] = annotations_dict
        self.categories_dict: List[dict] = categories_dict

        self.finalize()

    def set_annotation_entities(self):
        if self.annotation_type == AnnotationTypes.TWO_D_BOUNDING_BOX:
            self.__set_bounding_box_annotation_entities()
        elif self.annotation_type == AnnotationTypes.POLYGON:
            self.__set_polygon_annotation_entities()
        else:
            raise InvalidAnnotationError(
                f"invalid annotation type {self.annotation_type}"
            )

    def __set_bounding_box_annotation_entities(self):

        self.annotation_entities = []

        if not isinstance(self.annotations_dict, list):
            raise InvalidAnnotationError(
                "bounding box annotation is expected to be list"
            )

        for annotation in self.annotations_dict:
            try:
                category_id = annotation["category_id"]
                left = float(annotation["bbox"][0])
                top = float(annotation["bbox"][1])
                width = float(annotation["bbox"][2])
                height = float(annotation["bbox"][3])
            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            coordinates = [
                {"x": left, "y": top},
                {"x": left + width, "y": top},
                {"x": left + width, "y": top + height},
                {"x": left, "y": top + height},
            ]
            label = next(
                filter(lambda x: x["id"] == category_id, self.categories_dict)
            )["name"]
            self.annotation_entities.append(
                AnnotationEntity(
                    label=label,
                    category_id=category_id,
                    annotation_type=AnnotationTypes.TWO_D_BOUNDING_BOX,
                    coordinates=coordinates
                )
            )

    def __set_polygon_annotation_entities(self):
        if not isinstance(self.annotations_dict, list):
            raise InvalidAnnotationError(
                "Polygon annotations are expected to be a list"
            )
        self.annotation_entities = []
        for annotation in self.annotations_dict:
            category_id = annotation["category_id"]
            for coordinate_list in annotation["segmentation"]:
                coordinates = []
                iter_list = iter(coordinate_list)
                for x in iter_list:
                    y = next(iter_list)
                    coordinates.append({"x" : x, "y": y})
                label = next(
                    filter(lambda x: x["id"] == category_id, self.categories_dict)
                )["name"]
                self.annotation_entities.append(
                    AnnotationEntity(
                        label=label,
                        category_id=category_id,
                        coordinates=coordinates,
                        annotation_type=AnnotationTypes.POLYGON,
                    )
                )


