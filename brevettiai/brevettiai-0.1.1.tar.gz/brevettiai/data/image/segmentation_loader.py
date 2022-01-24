import logging

import numpy as np
import tensorflow as tf

from brevettiai.interfaces import vue_schema_utils as vue
from brevettiai.data.image import utils, ImageKeys
import json


log = logging.getLogger(__name__)


class SegmentationLoader(vue.VueSettingsModule):
    def __init__(self, classes: list, mapping: dict = None,
                 image_pipeline=None, sparse=False,
                 input_key="segmentation_path", output_key="segmentation"):
        self.input_key = input_key
        self.output_key = output_key
        self.classes = classes
        self.mapping = mapping
        self.sparse = sparse
        self._ip = image_pipeline

    def set_image_pipeline(self, image_pipeline):
        self._ip = image_pipeline

    @classmethod
    def to_schema(cls, builder, name, ptype, default, **kwargs):
        if name in {"input_key", "output_key", "image_pipeline"}:
            return
        if name == "classes":
            kwargs["label"] = "Segmentation classes"
        if name == "mapping":
            kwargs["label"] = "Segmentation mapping"
        return super().to_schema(builder, name, ptype, default, **kwargs)

    def build_label_space(self, sparse=None):
        sparse = sparse or self.sparse
        # Setup possible values
        if sparse:
            def get_output(x, output=np.arange(len(self.classes))[:, None]):
                try:
                    return output[self.classes.index(x)]
                except ValueError:
                    return None

        else:
            def get_output(x, output=np.eye(len(self.classes))):
                try:
                    if isinstance(x, str):
                        x = x.split("|")
                    return sum(output[self.classes.index(v)] for v in x)
                except ValueError:
                    return None

        # Build mapping
        if self.mapping:
            label_space = {k: get_output(v) for k, v in self.mapping.items()}
        else:
            label_space = {k: get_output(k) for k in self.classes}

        log.info(f"Invalid classes in map: {json.dumps({k: v for k, v in label_space.items() if v is None})}")
        label_space = {k: v for k, v in label_space.items() if v is not None}
        return label_space

    def load_segmentations(self, paths, input_image_shape, metadata):
        ip = self._ip
        crops_joiner, output_dtype = ip.get_output_spec(ip.rois, ip.roi_mode, dtype=tf.float32)
        label_space = self.build_label_space()
        segmentation_channels = 1 if self.sparse else len(self.classes)

        @tf.function
        def _load_segmentation(x):
            path, shape, metadata = x
            if tf.strings.length(path) > 0:
                # Load
                img = utils.load_segmentation(path, metadata, shape=(shape[0], shape[1], segmentation_channels),
                                              label_space=label_space, io=ip._io)

                # Apply ROIs
                crops = utils.roi_selection(img, rois=ip.rois, crops_joiner=crops_joiner)

                # Transform crops
                crops = [utils.image_view_transform(crop, target_size=ip.target_size,
                                                    resize_method="nearest",
                                                    keep_aspect_ratio=ip.keep_aspect_ratio,
                                                    antialias=ip.antialias,
                                                    padding_mode=ip.padding_mode) for crop in crops]

                return tuple(crops) if isinstance(output_dtype, tuple) else crops[0]
            else:
                return tf.zeros((1, 1, segmentation_channels))

        segmentations = tf.map_fn(_load_segmentation, [paths, input_image_shape, metadata], dtype=output_dtype)

        return segmentations

    def __call__(self, x, *args, **kwargs):
        metakeys = {ImageKeys.BOUNDING_BOX, ImageKeys.ZOOM}
        metadata = {k: x[k] for k in metakeys if k in x}
        segmentations = self.load_segmentations(x[self.input_key], x["_image_file_shape"], metadata)
        x[self.output_key] = segmentations
        return x
