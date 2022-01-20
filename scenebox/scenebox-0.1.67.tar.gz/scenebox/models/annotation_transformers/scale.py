#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

from typing import Optional

from shared.external.constants import (AnnotationMediaTypes,
                                       AnnotationProviders, AnnotationTypes, AssetsConstants, AnnotationGroups)
from shared.external.custom_exceptions import InvalidAnnotationError
from shared.external.models.annotation import Annotation, AnnotationEntity
from shared.external.models.object_access import ObjectAccess
from shared.external.tools import time_utils


class ScaleAnnotation(Annotation):
    def __init__(
            self,
            scale_response: dict,
            version: Optional[str] = None):

        self.scale_response = scale_response
        self.scaleapi_task = scale_response.get('task', {})
        self.scaleapi_params = self.scaleapi_task.get('params', {})
        self.scaleapi_type = self.scaleapi_task.get('type')
        self.metadata = self.scaleapi_task.get('metadata', {})
        self.scaleapi_annotations = scale_response.get(
            'response', {}).get('annotations', {})

        if self.scaleapi_type == 'lidarannotation':
            media_type = AssetsConstants.LIDARS_ASSET_ID
        else:
            media_type = AssetsConstants.IMAGES_ASSET_ID

        self.sets = [self.metadata.get("output_set_id")]
        if self.scaleapi_type == 'annotation':
            annotation_type = AnnotationTypes.TWO_D_BOUNDING_BOX
        elif self.scaleapi_type == 'segmentannotation':
            annotation_type = AnnotationTypes.SEGMENTATION
        elif self.scaleapi_type == 'polygonannotation':
            annotation_type = AnnotationTypes.POLYGON
        elif self.scaleapi_type == 'imageannotation':
            annotation_type = AnnotationTypes.LINE
        elif self.scaleapi_type == 'lidarannotation':
            annotation_type = AnnotationTypes.CUBOID
        else:
            raise InvalidAnnotationError(
                'invalid annotation type {}'.format(
                    self.scaleapi_type))

        super().__init__(
            annotation_meta=scale_response,
            asset_id=self.metadata.get("asset_id"),
            annotation_type=annotation_type,
            media_type=media_type,
            provider=AnnotationProviders.SCALE,
            version=version,
            annotation_group=AnnotationGroups.GROUND_TRUTH,
            id=scale_response.get('task_id') + ".ann",
            timestamp=time_utils.string_to_datetime(self.scaleapi_task.get('created_at')),
            set_id=self.metadata.get("output_set_id")
        )

        self.scaleapi_annotations = scale_response.get(
            'response', {}).get('annotations', {})

        if self.scaleapi_task.get('status') != 'completed':
            raise InvalidAnnotationError(
                'status {} is not completed'.format(
                    self.scaleapi_task.get('status')))

        self.finalize()

    def set_annotation_entities(self):
        if self.scaleapi_type == 'annotation':
            self.__set_bounding_box_annotation_entities()
        elif self.scaleapi_type == 'segmentannotation':
            self.__set_segmentation_annotation_entities()
        elif self.scaleapi_type == 'polygonannotation':
            self.__set_polygon_annotation_entities()
        elif self.scaleapi_type == 'imageannotation':
            self.__set_line_annotation_entities()
        elif self.scaleapi_type == 'lidarannotation':
            self.__set_lidar_annotation_entities()
        else:
            raise InvalidAnnotationError(
                'invalid annotation type {}'.format(
                    self.scaleapi_type))

    def __set_bounding_box_annotation_entities(self):

        self.annotation_entities = []

        if not isinstance(self.scaleapi_annotations, list):
            raise InvalidAnnotationError(
                'bounding box annotation is expected to be list')

        for scaleapi_annotation in self.scaleapi_annotations:
            try:
                width = scaleapi_annotation['width']
                height = scaleapi_annotation['height']
                left = scaleapi_annotation['left']
                top = scaleapi_annotation['top']
                label = scaleapi_annotation['label']
            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            coordinates = [
                {
                    'x': left,
                    'y': top
                },
                {
                    'x': left + width,
                    'y': top
                },
                {
                    'x': left + width,
                    'y': top + height
                },
                {
                    'x': left,
                    'y': top + height
                }
            ]
            self.annotation_entities.append(AnnotationEntity(
                label=label,
                annotation_type=AnnotationTypes.TWO_D_BOUNDING_BOX,
                coordinates=coordinates,
                attributes=scaleapi_annotation.get('attributes')
            ))

    def __set_segmentation_annotation_entities(self):

        if not isinstance(self.scaleapi_annotations, dict):
            raise InvalidAnnotationError(
                'bounding box annotation is expected to be dict')

        self.annotation_entities = []

        if 'unlabeled' in self.scaleapi_annotations:
            mask_object_access = ObjectAccess(
                        url=self.scaleapi_annotations['unlabeled'])
            self.masks.append(mask_object_access)
            self.annotation_entities.append(
                # TODO mask color needs to be specified here
                AnnotationEntity(
                    label='unlabeled',
                    annotation_type=AnnotationTypes.SEGMENTATION,
                    mask_id=mask_object_access.id,
                    mask_color="#ffffff"
                )
            )

        labeled_dic = self.scaleapi_annotations.get('labeled', {})
        for label in labeled_dic:
            value = labeled_dic[label]
            if isinstance(value, list):
                for url in value:
                    mask_object_access = ObjectAccess(url=url)
                    self.masks.append(mask_object_access)
                    # TODO mask color needs to be specified here
                    self.annotation_entities.append(AnnotationEntity(
                        label=label,
                        annotation_type=AnnotationTypes.SEGMENTATION,
                        mask_id=mask_object_access.id,
                        mask_color="#ffffff")
                    )
            else:
                mask_object_access = ObjectAccess(url=value)
                self.masks.append(mask_object_access)
                # TODO mask color needs to be specified here
                self.annotation_entities.append(AnnotationEntity(
                    label=label,
                    annotation_type=AnnotationTypes.SEGMENTATION,
                    mask_id=mask_object_access.id,
                    mask_color="#ffffff")
                )

    def __set_polygon_annotation_entities(self):
        self.annotation_entities = []

        if not isinstance(self.scaleapi_annotations, list):
            raise InvalidAnnotationError(
                'polygon annotation is expected to be list')

        for scaleapi_annotation in self.scaleapi_annotations:
            try:
                coordinates = scaleapi_annotation['vertices']
                key = scaleapi_annotation.get('key')
                label = scaleapi_annotation['label']
            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            self.annotation_entities.append(AnnotationEntity(
                label=label,
                annotation_type=AnnotationTypes.POLYGON,
                coordinates=coordinates,
                attributes=scaleapi_annotation.get('attributes'),
                uid=key
            ))

    def __set_line_annotation_entities(self):
        self.annotation_entities = []

        if not isinstance(self.scaleapi_annotations, list):
            raise InvalidAnnotationError(
                'line annotation is expected to be list')

        for scaleapi_annotation in self.scaleapi_annotations:
            try:
                coordinates = scaleapi_annotation['vertices']
                key = scaleapi_annotation['key']
                label = scaleapi_annotation['label']
            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            self.annotation_entities.append(AnnotationEntity(
                label=label,
                annotation_type=AnnotationTypes.LINE,
                coordinates=coordinates,
                attributes=scaleapi_annotation.get('attributes'),
                uid=key
            ))

    def __set_lidar_annotation_entities(self):

        self.annotation_entities = []

        if not isinstance(self.scaleapi_annotations, list):
            raise InvalidAnnotationError(
                'lidar annotation is expected to be list')

        for scaleapi_annotation in self.scaleapi_annotations:
            try:
                width = scaleapi_annotation['width']
                height = scaleapi_annotation['height']
                left = scaleapi_annotation['left']
                top = scaleapi_annotation['top']
                label = scaleapi_annotation['label']
            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            coordinates = [
                {
                    'x': left,
                    'y': top
                },
                {
                    'x': left + width,
                    'y': top
                },
                {
                    'x': left + width,
                    'y': top + height
                },
                {
                    'x': left,
                    'y': top + height
                }
            ]
            self.annotation_entities.append(AnnotationEntity(
                label=label,
                annotation_type=AnnotationTypes.CUBOID,
                coordinates=coordinates,
                attributes=scaleapi_annotation.get('attributes')
            ))
