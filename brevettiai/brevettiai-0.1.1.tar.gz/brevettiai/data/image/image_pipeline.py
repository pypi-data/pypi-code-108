import functools
import logging

import numpy as np
import tensorflow as tf

from brevettiai.data.image import utils
from brevettiai.io import io_tools
from brevettiai.interfaces import vue_schema_utils as vue
from brevettiai.data.image.segmentation_loader import SegmentationLoader
from brevettiai.data.image import ImageKeys

log = logging.getLogger(__name__)

COLOR_CHANNELS = {
    "greyscale": 1,
    "bayer": 3,
    "rgb": 3
}

RESCALE_METHODS = {
    "None": dict(scale=1.0, offset=0),
    "imagenet": dict(scale=1 / 127.5, offset=-1),
    "unit": dict(scale=1 / 255, offset=0),
}

class ImagePipeline(vue.VueSettingsModule):
    ROI_MODE = {
        "concatenate_height": functools.partial(tf.concat, axis=0),
        "as_timeseries": functools.partial(tf.stack, axis=0)
    }
    ROI_MODE_CONCAT_HEIGHT = "concatenate_height"
    ROI_MODE_TIMESERIES = "as_timeseries"

    def __init__(self, target_size: tuple = None, rois: tuple = None, roi_mode: str = "concatenate_height",
                 path_key: str = "path", output_key: str = "img",
                 color_mode: str= "rgb", segmentation: SegmentationLoader = None,
                 keep_aspect_ratio=False, rescale: str = None, resize_method: str = tf.image.ResizeMethod.BILINEAR,
                 antialias: bool = False, padding_mode: str = "CONSTANT", center_padding: bool = False,
                 io=io_tools):
        """
        :param target_size: target size of images
        :param rois: Region of interest(s) (((x11,y11),(x12,y12)),..., ((xn1,yn1),(xn2,yn2)))
        :param roi_mode: Treatment of rois (None, ROI_MODE_CONCAT_HEIGHT, ROI_MODE_TIMESERIES)
        :param path_key:
        :param output_key:
        :param color_mode: Color mode of images (greyscale, bayer, rgb)
        :param segmentation: SegmentationLoader arguments or object
        :param keep_aspect_ratio: keep the aspect ratio during resizing of image
        :param rescale: rescaling mode (None [0,255], imagenet [-1,1], unit [0,1])
        :param resize_method: resizing method
        :param antialias: Apply antialiasing when scaling
        :param padding_mode: Padding mode (CONSTANT, REFLECT, SYMMETRIC) applied with tf.pad
        :param center_padding: Determine if padding should be centered
        :param io:
        :param kwargs:
        """

        self._io = io
        self.path_key = path_key
        self.output_key = output_key

        # Format rois and check validity
        assert roi_mode is None or roi_mode in ImagePipeline.ROI_MODE or len(rois) == 0
        self.roi_mode = roi_mode
        if rois is None or len(rois) == 0:
            self.rois = None
        else:
            self.rois = np.array(rois)
            if self.rois.ndim == 2:
                self.rois = self.rois[None]
            assert self.rois.ndim == 3

        # Format target_size and check validity
        assert target_size is None or len(target_size) == 2, "Target size should consist of height/width"
        self.target_size = target_size

        # Transformation arguments
        self.color_mode = color_mode
        self.keep_aspect_ratio = keep_aspect_ratio
        self.rescale = rescale
        self.resize_method = resize_method
        self.antialias = antialias
        self.padding_mode = padding_mode
        self.center_padding = center_padding

        # Segmentation module
        self.segmentation = segmentation

    @property
    def segmentation(self):
        return self._segmentation

    @segmentation.setter
    def segmentation(self, segmentation):
        if isinstance(segmentation, dict):
            self._segmentation = SegmentationLoader.from_config(segmentation)
        else:
            self._segmentation = segmentation
        if isinstance(self._segmentation, SegmentationLoader):
            self._segmentation.set_image_pipeline(self)

    @staticmethod
    def get_output_spec(rois, roi_mode, dtype=tf.float32):
        outputs_count = 1 if rois is None else len(rois)
        crops_joiner = ImagePipeline.ROI_MODE.get(roi_mode)
        dtypes = outputs_count * (dtype,) if crops_joiner is None else dtype
        return crops_joiner, dtypes

    @property
    def output_shape(self):
        if self.target_size is None:
            return None, None, COLOR_CHANNELS[self.color_mode]
        else:
            return (*self.target_size, COLOR_CHANNELS[self.color_mode])

    @classmethod
    def to_settings(cls, config):
        if config["target_size"] is not None:
            config["input_height"], config["input_width"] = config["target_size"]
        config.pop("target_size")
        return super().to_settings(config)

    @classmethod
    def from_config(cls, config):
        # Legacy code to load old ModelMeta
        if "input_shape" in config:
            config["target_size"] = config["input_shape"]
            config.pop("input_shape")
        config.pop("augmentation", None)
        return super().from_config(config)

    @classmethod
    def to_config(cls, settings):
        if "input_shape" in settings:
            settings["target_size"] = settings["input_shape"]
            settings.pop("input_shape")
        if "target_size" not in settings:
            if "input_height" in settings:
                settings["target_size"] = settings["input_height"], settings["input_width"]
                settings.pop("input_width")
                settings.pop("input_height")
        settings.pop("augmentation", None)
        return super().to_config(settings)

    @classmethod
    def to_schema(cls, builder, name, ptype, default, **kwargs):
        from brevettiai.interfaces import vue_schema_utils as vue

        if name == "target_size":
            builder.add_field(vue.number_input(label="Input height", model="input_height", default=224, min=96, max=4096))
            builder.add_field(vue.number_input(label="Input width", model="input_width", default=224, min=96, max=4096))
        elif name == "color_mode":
            builder.add_field(vue.select("Color mode", name, required=False, default=default,
                       values=list(COLOR_CHANNELS.keys())),)
        elif name == "rois":
            builder.add_field(
                vue.text_input("Image rois. E.g. [[[100, 100], [400, 500]], [[500, 100], [800, 500]]]", name,
                               required=False, default=[], json=True),
            )
        elif name == "rescale":
            builder.add_field(vue.select("Rescaling", name, required=False, default=str(default),
                                         values=["None", *RESCALE_METHODS.keys()] ))
        elif name in {"path_key", "output_key", "io", "kwargs"}:
            return
        else:
            return super().to_schema(builder=builder, name=name, ptype=ptype, default=default, **kwargs)

    def load_images(self, paths, metadata):
        """
        Load batch of images given tensor of paths
        """
        channels = COLOR_CHANNELS.get(self.color_mode, 3)
        crops_joiner, output_dtype = ImagePipeline.get_output_spec(self.rois, self.roi_mode)
        output_dtype = (tf.int32, output_dtype)
        rescaling = self.get_rescaling()

        @tf.function
        def _load_image(x):
            path, metadata = x
            # Load
            img = utils.load_image(path, metadata=metadata, channels=channels, color_mode=self.color_mode, io=self._io)

            # Prepare
            img = tf.cast(img, tf.float32)
            input_shape = tf.convert_to_tensor(tf.shape(img))

            # Apply ROIs
            crops = utils.roi_selection(img, rois=self.rois, crops_joiner=crops_joiner)

            # Transform crops
            crops = [utils.image_view_transform(crop, target_size=self.target_size,
                                                scale=rescaling["scale"], offset=rescaling["offset"],
                                                resize_method=self.resize_method,
                                                keep_aspect_ratio=self.keep_aspect_ratio,
                                                antialias=self.antialias,
                                                padding_mode=self.padding_mode,
                                                center_padding=self.center_padding) for crop in crops]

            # Output
            crops = (tuple(crops) if isinstance(output_dtype[1], tuple) else crops[0])
            return input_shape, crops

        input_shapes, imgs = tf.map_fn(_load_image, [paths, metadata], dtype=output_dtype)

        return input_shapes, imgs

    def get_rescaling(self):
        '''
            returns scale, offset
        '''
        if self.rescale is None:
            return dict(scale=1, offset=0)
        elif isinstance(self.rescale, str):
            return RESCALE_METHODS.get(self.rescale, )
        return self.rescale

    def __call__(self, x, *args, **kwargs):
        metadata = {k: x[k] for k in {ImageKeys.BOUNDING_BOX, ImageKeys.ZOOM, ImageKeys.SIZE} if k in x}
        input_shape, img = self.load_images(x[self.path_key], metadata)

        x["_image_file_shape"] = input_shape
        x[self.output_key] = img

        if self.segmentation is not None and self.segmentation.classes:
            x = self.segmentation(x)
        return x
