#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
import io
from datetime import datetime
from typing import Dict, List, NamedTuple, Optional, Tuple

from ..clients import AssetManagerClient
from ..constants import (AnnotationMediaTypes, AnnotationTypes, AssetsConstants, AnnotationGroups)
from ..custom_exceptions import InvalidAnnotationError
from ..tools import misc, time_utils
from ..tools.logger import get_logger
from .object_access import ObjectAccess

logger = get_logger(__name__)


class Point(NamedTuple):
    left: float
    top: float
    label: str
    category_id: Optional[int] = None
    confidence: Optional[float] = None
    geometry: Optional[str] = None
    attributes: Optional[dict] = None


class BoundingBox(NamedTuple):
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    label: str
    category_id: Optional[int] = None
    confidence: Optional[float] = None
    attributes: Optional[dict] = None


class Polygon(NamedTuple):
    coordinates: List[Tuple[float, float]]
    label: str
    category_id: Optional[int] = None
    confidence: Optional[float] = None
    attributes: Optional[dict] = None


class Line(NamedTuple):
    coordinates: List[Tuple[float, float]]
    label: str
    complete: Optional[bool] = False
    category_id: Optional[int] = None
    confidence: Optional[float] = None
    attributes: Optional[dict] = None


class Label(NamedTuple):
    label: str
    class_name: Optional[str] = None
    category_id: Optional[int] = None
    confidence: Optional[float] = None


class Pose(NamedTuple):
    label: str
    keypoints: List[Point]
    keypoint_names: List[str]
    attributes: Optional[dict] = None


class Annotation(object):
    def __init__(self, **kwargs):
        self.id: str = kwargs.get("id", misc.get_guid())
        self.timestamp: datetime = kwargs.get("timestamp", datetime.utcnow())

        self.asset_id: str = kwargs.get("asset_id") or kwargs.get("image_id") or \
                             kwargs.get("video_id") or kwargs.get("lidar_id")
        if not self.asset_id:
            raise InvalidAnnotationError("asset_id (image, video, lidar) should be specified")

        self.media_type: str = kwargs.get("media_type", AssetsConstants.IMAGES_ASSET_ID)
        if self.media_type not in AnnotationMediaTypes.VALID_TYPES:
            raise InvalidAnnotationError(
                "invalid annotation type {}".format(self.media_type)
            )

        self.annotation_type: str = kwargs.get("annotation_type")
        if self.annotation_type not in AnnotationTypes.VALID_TYPES:
            raise InvalidAnnotationError(
                "invalid annotation type {}".format(self.annotation_type)
            )

        self.provider: Optional[str] = kwargs.get("provider")
        self.annotation_entities: List[AnnotationEntity] = kwargs.get("annotation_entities", [])
        self.annotation_meta: Dict = kwargs.get("annotation_meta", {})
        self.sets: List[str] = kwargs.get("sets", [])
        if "set_id" in kwargs:
            self.sets.append(kwargs.get("set_id"))
        self.session_uid: Optional[str] = kwargs.get("session_uid")
        self.sensor: Optional[str] = kwargs.get("sensor")
        self.version: Optional[str] = kwargs.get("version")
        self.annotation_group: str = kwargs.get("annotation_group", AnnotationGroups.GROUND_TRUTH)
        self.masks: List[ObjectAccess] = kwargs.get("masks", [])
        self.tags: List[str] = kwargs.get("tags", [])
        self.frame: Optional[int] = kwargs.get("frame")
        if self.media_type in [AssetsConstants.VIDEOS_ASSET_ID] and self.frame is None:
            raise InvalidAnnotationError(
                "{} annotation need frame".format(self.media_type)
            )

    def set_asset_id(self, asset_id: str):
        self.asset_id = asset_id

    def finalize(self):
        self.set_annotation_entities()
        self.__sanity_check()

    def set_annotation_entities(self):
        pass

    def post_upload(self, annotations_amc: AssetManagerClient):
        pass

    def __sanity_check(self):
        pass

    def to_dic(self):
        """
        return a dictionary object representative of Annotation
        :return: dictionary object
        """
        annotation_entities_ = []
        labels = set()
        for annotation_entity in self.annotation_entities:
            annotation_entities_.append(annotation_entity.to_dic())
            labels.add(annotation_entity.label)
        return {
            "session_uid": self.session_uid,
            "timestamp": time_utils.datetime_or_str_to_iso_utc(self.timestamp),
            "asset_id": self.asset_id,
            "media_type": self.media_type,
            "provider": self.provider,
            "annotation_type": self.annotation_type,
            "annotation_entities": annotation_entities_,
            "sets": self.sets,
            "labels": list(labels),
            "sensor": self.sensor,
            "version": self.version,
            "annotation_group": self.annotation_group,
            "masks": [_.to_dic() for _ in self.masks],
            "frame": self.frame,
            "tags": self.tags
        }


class RelatedAnnotation(object):
    # initialize a related annotation object(
    def __init__(self, related_annotation_dic):
        try:
            # annotation label
            self.uid = related_annotation_dic["uid"]

            # the unique (worldwide) id of the entity
            self.relationship = related_annotation_dic["relationship"]
            if self.relationship not in {"parent", "child", "sibling"}:
                raise InvalidAnnotationError(
                    "unrecognized relation {}".format(self.relationship)
                )

        except KeyError as e:
            raise InvalidAnnotationError(str(e))

    def to_dic(self):
        """
        return a dictionary object representative of Annotation entity
        :return: dictionary object
        """
        return {"uid": self.uid, "relationship": self.relationship}


class AnnotationEntity(object):
    # initialize an annotation object (a single annotation such as tire,
    # pedestrian, etc)
    def __init__(self,
                 label: str,
                 annotation_type: str,
                 class_name: Optional[str] = None,
                 coordinates: Optional[List] = None,
                 confidence: Optional[float] = None,
                 mask_color: Optional[str] = None,
                 mask_id: Optional[str] = None,
                 uid: Optional[str] = None,
                 category_id: Optional[int] = None,
                 related_annotations: Optional[List[RelatedAnnotation]] = None,
                 attributes: Optional[dict] = None,
                 mask_type: Optional[str] = None,
                 composition: Optional[List[Dict[str, Point]]] = None):

        # annotation label
        self.label = label
        self.category_id = category_id
        self.class_name = class_name
        if mask_color:
            self.mask_color = mask_color.lower()
            if not misc.is_valid_hex(self.mask_color):
                raise InvalidAnnotationError(
                    "invalid hex color {}".format(mask_color))
        else:
            self.mask_color = None

        # the unique (worldwide) id of the entity
        self.uid = uid or misc.get_guid()

        self.mask_id = mask_id

        if isinstance(confidence, float):
            self.confidence = confidence
            if self.confidence < 0 or self.confidence > 1:
                raise InvalidAnnotationError(
                    "confidence {} should be between 0 and 1".format(
                        self.confidence))
        elif confidence is None:
            self.confidence = None
        else:
            raise InvalidAnnotationError(
                "invalid confidence format {}".format(type(confidence))
            )

        if annotation_type not in AnnotationTypes.VALID_TYPES:
            raise InvalidAnnotationError(
                "invalid annotation type {}".format(annotation_type)
            )
        else:
            self.annotation_type = annotation_type

        # x, y coordinates
        self.coordinates = []

        for point in coordinates or []:
            self.coordinates.append(
                {"x": float(point["x"]), "y": float(point["y"])})

        # coordinate checks for various geometry types:
        if self.annotation_type == AnnotationTypes.POINT and len(
                self.coordinates) != 1:
            raise InvalidAnnotationError(
                "point annotations should exactly have 1 point"
            )

        if self.annotation_type == AnnotationTypes.TWO_D_BOUNDING_BOX and len(
                self.coordinates) != 4:
            raise InvalidAnnotationError(
                "bounding_box annotations should exactly have 4 points"
            )

        if self.annotation_type in {
                AnnotationTypes.POLYGON,
                AnnotationTypes.LINE} and not self.coordinates:
            raise InvalidAnnotationError(
                "empty coordinates for annotation_type = {}".format(
                    self.annotation_type))

        if self.annotation_type == AnnotationTypes.SEGMENTATION and not self.mask_color:
            raise InvalidAnnotationError(
                "mask color should be specified for segmentation"
            )

        # get all related_annotations
        self.related_annotations = []

        for related_annotation in related_annotations or []:
            self.related_annotations.append(
                RelatedAnnotation(related_annotation))

        # optional attributes of an entity
        self.attributes = attributes or {}

        self.mask_type = mask_type

        # composition makes sense for key point annotations only
        self.composition = composition or []
        if self.composition and self.annotation_type not in [AnnotationTypes.TWO_D_POSE]:
            raise InvalidAnnotationError("composition {} cannot be defined for {}".format(
                self.composition,
                self.annotation_type)
            )

    def to_dic(self):
        """
        return a dictionary object representative of Annotation entity
        :return: dictionary object
        """
        related_annotations_ = []
        for related_annotation in self.related_annotations:
            related_annotations_.append(related_annotation.to_dic())

        dic = {
            "uid": self.uid,
            "label": self.label,
            "annotation_type": self.annotation_type,
            "attributes": self.attributes,
            "related_annotations": related_annotations_,
            "category_id": self.category_id,
        }
        if self.coordinates:
            dic["coordinates"] = self.coordinates
        if self.confidence:
            dic["confidence"] = self.confidence
        if self.mask_id:
            dic["mask_id"] = self.mask_id
        if self.mask_color:
            dic["mask_color"] = self.mask_color
        if self.class_name:
            dic["class_name"] = self.class_name
        if self.mask_type:
            dic["mask_type"] = self.mask_type
        if self.composition:
            composition_dict = []
            for item in self.composition:
                composition_dict.append({key: point._asdict() for key, point in item.items()})
            dic["composition"] = composition_dict
        return dic

    @classmethod
    def from_dict(cls, annotation_entity_dic: dict):

        confidence = annotation_entity_dic.get("confidence")
        if isinstance(confidence, float):
            if confidence < 0 or confidence > 1:
                raise InvalidAnnotationError(
                    "confidence {} should be between 0 and 1".format(
                        confidence))
        elif confidence is None:
            pass
        else:
            raise InvalidAnnotationError(
                "invalid confidence format {}".format(type(confidence))
            )

        coordinates = []

        try:
            for point in annotation_entity_dic.get("coordinates", []):
                coordinates.append(
                    {"x": float(point["x"]), "y": float(point["y"])})

        except KeyError:
            raise InvalidAnnotationError(str(KeyError))

        related_annotations = []
        for related_annotation in annotation_entity_dic.get(
                "related_annotations", []):
            related_annotations.append(RelatedAnnotation(related_annotation))

        composition = annotation_entity_dic.get("composition", [])
        composition_points = []
        for item in composition:
            composition_points.append({key: Point(**point_dict) for key, point_dict in item.items()})

        return cls(
            label=annotation_entity_dic["label"],
            category_id=annotation_entity_dic.get(
                "category_id"),
            uid=annotation_entity_dic.get("uid", misc.get_guid()),
            annotation_type=annotation_entity_dic["annotation_type"],
            mask_id=annotation_entity_dic.get("mask_id"),
            confidence=confidence,
            mask_color=annotation_entity_dic.get("mask_color"),
            coordinates=coordinates,
            attributes=annotation_entity_dic.get("attributes"),
            class_name=annotation_entity_dic.get("class_name"),
            related_annotations=related_annotations,
            composition=composition_points
        )

# TODO replace image_id with asset_id in all annotation classes


class SegmentationAnnotation(Annotation):
    def __init__(self,
                 labels: List[str],
                 mask_colors: List[str],
                 mask_urls: Optional[List[str]] = None,
                 mask_uris: Optional[List[str]] = None,
                 mask_file_paths: Optional[List[str]] = None,
                 mask_ids: Optional[List[str]] = None,
                 mask_types: Optional[List[str]] = None,
                 confidences: Optional[List[float]] = None,
                 **kwargs
                 ):
        super().__init__(annotation_type=AnnotationTypes.SEGMENTATION, **kwargs)
        self.labels = labels
        self.mask_urls = mask_urls or [None] * len(labels)
        self.mask_uris = mask_uris or [None] * len(labels)
        self.mask_ids = mask_ids or [None] * len(labels)
        self.mask_file_paths = mask_file_paths or [None] * len(labels)
        self.mask_colors = mask_colors
        self.mask_types = mask_types or [None] * len(labels)
        self.confidences = confidences or [None] * len(labels)
        self.mask_id_path_map = {}
        self.finalize()

    def post_upload(self, annotations_amc: AssetManagerClient):
        for mask_id, mask_file_path in self.mask_id_path_map.items():
            with open(mask_file_path, 'rb') as f:
                file_obj = io.BytesIO(f.read())
            annotations_amc.put_file(
                id=mask_id,
                file_object=file_obj,
                corr_asset_id=self.id,
                corr_asset_type=AssetsConstants.ANNOTATIONS_ASSET_ID,
                content_type="image/png"
            )

    def set_annotation_entities(self):
        self.annotation_entities = []
        assert len(self.labels) == len(self.mask_urls)
        assert len(self.labels) == len(self.confidences)
        assert len(self.labels) == len(self.mask_colors)
        assert len(self.labels) == len(self.mask_uris)
        assert len(self.labels) == len(self.mask_file_paths)
        assert len(self.labels) == len(self.mask_ids)
        assert len(self.labels) == len(self.mask_types)
        masks = set()
        for label, url, confidence, mask_color, uri, mask_id, mask_file_path, mask_type in zip(
                self.labels, self.mask_urls, self.confidences, self.mask_colors, self.mask_uris,
                self.mask_ids, self.mask_file_paths, self.mask_types):
            if url:
                object_access = ObjectAccess(url=url)
            elif uri:
                object_access = ObjectAccess(uri=uri)
            elif mask_file_path:
                mask_id = "{}".format(misc.get_guid())
                self.mask_id_path_map[mask_id] = mask_file_path
                object_access = ObjectAccess(id=mask_id)
            elif mask_id:
                object_access = ObjectAccess(id=mask_id)
            else:
                raise InvalidAnnotationError(
                    "either url or uri or mask file path should be specified for {}".format(
                        self.id))

            masks.add(object_access)
            self.annotation_entities.append(
                AnnotationEntity(
                    label=label,
                    annotation_type=AnnotationTypes.SEGMENTATION,
                    mask_id=object_access.id,
                    confidence=confidence,
                    mask_color=mask_color,
                    mask_type=mask_type or "MultiColor"
                )
            )
            self.masks = list(masks)


class BoundingBoxAnnotation(Annotation):
    def __init__(self, bounding_boxes: List[BoundingBox], **kwargs):
        super().__init__(annotation_type=AnnotationTypes.TWO_D_BOUNDING_BOX, **kwargs)
        self.bounding_boxes = bounding_boxes
        self.finalize()

    def set_annotation_entities(self):
        self.annotation_entities = []

        if not isinstance(self.bounding_boxes, list):
            raise InvalidAnnotationError(
                "bounding box annotation is expected to be list"
            )

        for bounding_box in self.bounding_boxes:
            if bounding_box.attributes:
                assert isinstance(bounding_box.attributes, dict), \
                    "attributes should be of type dict {} provided".format(type(bounding_box.attributes))
            if bounding_box.attributes:
                if bounding_box.attributes.get("track_id"):
                    assert isinstance(bounding_box.attributes["track_id"], int), \
                        "track_id should be of type int {} provided".format(type(bounding_box.attributes["track_id"]))
            try:
                category_id = bounding_box.category_id
                left = float(bounding_box.x_min)
                top = float(bounding_box.y_max)
                bottom = float(bounding_box.y_min)
                right = float(bounding_box.x_max)
            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            coordinates = [
                {"x": left, "y": bottom},
                {"x": right, "y": bottom},
                {"x": right, "y": top},
                {"x": left, "y": top},
            ]
            self.annotation_entities.append(
                AnnotationEntity(
                    label=bounding_box.label,
                    category_id=category_id,
                    annotation_type=AnnotationTypes.TWO_D_BOUNDING_BOX,
                    coordinates=coordinates,
                    confidence=bounding_box.confidence,
                    attributes=bounding_box.attributes
                )
            )


class PolygonAnnotation(Annotation):
    def __init__(self, polygons: List[Polygon], **kwargs):
        super().__init__(annotation_type=AnnotationTypes.POLYGON, **kwargs)
        self.polygons = polygons
        self.finalize()

    def set_annotation_entities(self):
        self.annotation_entities = []

        if not isinstance(self.polygons, list):
            raise InvalidAnnotationError(
                "polygon annotation is expected to be list"
            )

        for polygon in self.polygons:
            try:
                category_id = polygon.category_id
                coords_ = polygon.coordinates
            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            coordinates = []
            for c in coords_:
                coordinates.append({"x": c[0], "y": c[1]})
            self.annotation_entities.append(
                AnnotationEntity(
                    label=polygon.label,
                    category_id=category_id,
                    annotation_type=AnnotationTypes.POLYGON,
                    coordinates=coordinates,
                    confidence=polygon.confidence,
                    attributes=polygon.attributes
                )
            )



class PointAnnotation(Annotation):
    def __init__(self, points: List[Point], **kwargs):
        super().__init__(annotation_type=AnnotationTypes.POINT, **kwargs)
        self.points = points
        self.finalize()

    def set_annotation_entities(self):
        self.annotation_entities = []

        if not isinstance(self.points, list):
            raise InvalidAnnotationError(
                "point annotation is expected to be list"
            )

        for point in self.points:
            try:
                category_id = point.category_id
                left = float(point.left)
                top = float(point.top)

            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            coordinates = [
                {"x": left, "y": top}
            ]

            self.annotation_entities.append(
                AnnotationEntity(
                    label=point.label,
                    category_id=category_id,
                    annotation_type=AnnotationTypes.POINT,
                    coordinates=coordinates,
                    confidence=point.confidence,
                    attributes=point.attributes
                )
            )


class LineAnnotation(Annotation):
    def __init__(self, lines: List[Line], **kwargs):
        super().__init__(annotation_type=AnnotationTypes.LINE, **kwargs)
        self.lines = lines
        self.finalize()

    def set_annotation_entities(self):
        self.annotation_entities = []

        if not isinstance(self.lines, list):
            raise InvalidAnnotationError(
                "line annotation is expected to be list"
            )

        for line in self.lines:
            try:
                category_id = line.category_id
                coords_ = line.coordinates
            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            coordinates = []
            for c in coords_:
                coordinates.append({"x": c[0], "y": c[1]})

            self.annotation_entities.append(
                AnnotationEntity(
                    label=line.label,
                    category_id=category_id,
                    annotation_type=AnnotationTypes.LINE,
                    coordinates=coordinates,
                    confidence=line.confidence,
                    attributes=line.attributes
                )
            )


class ClassificationAnnotation(Annotation):
    def __init__(self, labels: List[Label], **kwargs):
        super().__init__(annotation_type=AnnotationTypes.CLASSIFICATION, **kwargs)
        self.labels = labels
        self.finalize()

    def set_annotation_entities(self):
        self.annotation_entities = []
        for label in self.labels:
            self.annotation_entities.append(
                AnnotationEntity(
                    label=label.label,
                    category_id=label.category_id,
                    class_name=label.class_name,
                    annotation_type=AnnotationTypes.CLASSIFICATION,
                    confidence=label.confidence
                )
            )


class PersonPose(Pose):
    keypoint_names = ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
                      'left_shoulder', 'right_shoulder', 'left_elbow',
                      'right_elbow', 'left_wrist', 'right_wrist', 'left_hip',
                      'right_hip', 'left_knee', 'right_knee', 'left_ankle',
                      'right_ankle']

    def __new__(cls, keypoints: List[Point],
                keypoint_names: Optional[List[str]] = keypoint_names,
                attributes: Optional[dict] = None):

        label = "person"
        self = super(PersonPose, cls).__new__(cls, label,
                                              keypoints,
                                              keypoint_names,
                                              attributes)
        return self


class PoseAnnotation(Annotation):
    def __init__(self, poses: List[Pose], **kwargs):
        super().__init__(annotation_type=AnnotationTypes.TWO_D_POSE, **kwargs)
        self.poses = poses
        self.finalize()

    def set_annotation_entities(self):
        self.annotation_entities = []

        if not isinstance(self.poses, list):
            raise InvalidAnnotationError(
                "pose annotation is expected to be a list"
            )

        for pose in self.poses:
            assert len(pose.keypoint_names) == len(pose.keypoints)

            composition = []
            for i, keypoint_name in enumerate(pose.keypoint_names):
                try:
                    composition.append({
                        keypoint_name: pose.keypoints[i]
                    })
                except KeyError as e:
                    raise InvalidAnnotationError(str(e))

            self.annotation_entities.append(
                AnnotationEntity(
                    label=pose.label,
                    composition=composition,
                    annotation_type=AnnotationTypes.TWO_D_POSE,
                    attributes=pose.attributes
                )
            )

