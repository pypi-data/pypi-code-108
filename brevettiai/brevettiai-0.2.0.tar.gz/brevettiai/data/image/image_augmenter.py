import logging
import tensorflow as tf
import tensorflow_addons as tfa
import numpy as np
from brevettiai.data.image import ImageKeys
from brevettiai.interfaces import vue_schema_utils as vue
from functools import partial

log = logging.getLogger(__name__)


@tf.function
def _gaussian_kernel(kernel_size, sigma, dtype):
    x = tf.range(-kernel_size // 2, kernel_size // 2 + 1, dtype=dtype)
    g = tf.math.exp(-(tf.pow(x, 2) / (2 * tf.pow(tf.cast(sigma, dtype), 2))))
    g_kernel = tf.tensordot(g, g, axes=0)
    return g_kernel / tf.reduce_sum(g_kernel)


@tf.function
def gaussian_blur(x, sigma):
    kernel_size = tf.cast(tf.math.ceil(sigma * 2.5), tf.int32) * 2 + 1
    gaussian_blur_kernel = tf.tile(_gaussian_kernel(kernel_size, sigma, x.dtype)[..., None, None],
                                   (1, 1, tf.shape(x)[-1], 1))
    x = tf.nn.depthwise_conv2d(x, gaussian_blur_kernel, [1, 1, 1, 1], 'SAME')
    return x


@tf.function
def _avg_kernel(kernel_size, dtype):
    g_kernel = tf.ones(kernel_size, dtype=dtype)
    return g_kernel / tf.reduce_sum(g_kernel)


@tf.function
def affine(o1, o2, r1, r2, sc, a, sh1, sh2, t1, t2):
    """
    Create N affine transform matrices from output to input (Nx3x3)
    for use with tfa.transform
    :param o1: Origin 1 (shape / 2 for center)
    :param o2: Origin 2
    :param r1: Reference scale 1 (1 or -1 for flip)
    :param r2: Reference scale 1
    :param sc: Augmented scale
    :param a: Rotation in radians
    :param sh1: Shear 1
    :param sh2: Shear 2
    :param t1: Translate 1
    :param t2: Translate 2
    :return: Inverse transformation matrix
    """
    _0 = tf.zeros_like(o1)
    _1 = tf.ones_like(o1)
    T1 = tf.transpose(tf.convert_to_tensor([[_1, _0, -(o2 - 1)],
                                            [_0, _1, -(o1 - 1)],
                                            [_0, _0, _1]], dtype=tf.float32), [2, 0, 1])
    T2 = tf.transpose(tf.convert_to_tensor([[_1, _0, (o2 - 1)],
                                            [_0, _1, (o1 - 1)],
                                            [_0, _0, _1]], dtype=tf.float32), [2, 0, 1])
    ref = tf.transpose(tf.convert_to_tensor([[r2, _0, _0],
                                             [_0, r1, _0],
                                             [_0, _0, _1]], dtype=tf.float32), [2, 0, 1])
    scale = tf.transpose(tf.convert_to_tensor([[1 + sc, _0, _0],
                                               [_0, 1 + sc, _0],
                                               [_0, _0, _1]], dtype=tf.float32), [2, 0, 1])
    rot = tf.transpose(tf.convert_to_tensor([[tf.cos(a), -tf.sin(a), _0],
                                             [tf.sin(a), tf.cos(a), _0],
                                             [_0, _0, _1]], dtype=tf.float32), [2, 0, 1])
    she = tf.transpose(tf.convert_to_tensor([[_1, sh2, _0],
                                             [sh1, _1, _0],
                                             [_0, _0, _1]], dtype=tf.float32), [2, 0, 1])
    tra = tf.transpose(tf.convert_to_tensor([[_1, _0, t2],
                                             [_0, _1, t1],
                                             [_0, _0, _1]], dtype=tf.float32), [2, 0, 1])
    return T2 @ tra @ she @ ref @ scale @ rot @ T1


class RandomTransformer(vue.VueSettingsModule):
    def __init__(self, chance: float = 0.5, flip_up_down: bool = True, flip_left_right: bool = True,
                 scale: float = 0.2, rotate_chance: float = 0.5, rotate: float = 90,
                 translate_horizontal: float = 0.1, translate_vertical: float = 0.1, shear: float = 0.04,
                 interpolation: str = "bilinear"):
        """
        Build random transformation matrices for batch of images
        :param shape:
        :param chance:
        :param flip:
        :param scale:
        :param rotate:
        :param translate:
        :param shear:
        :param interpolation: Resampling interpolation method
        :return:
        """

        self.chance = chance
        self.flip_up_down = flip_up_down
        self.flip_left_right = flip_left_right
        self.scale = scale
        self.rotate_chance = rotate_chance
        self.rotate = rotate
        self.translate_horizontal = translate_horizontal
        self.translate_vertical = translate_vertical
        self.shear = shear
        self.interpolation = interpolation
        self.fill_seg_value = 0.0

    def set_fill_seg_value(self, fill_value):
        self.fill_seg_value = fill_value

    def transform_images(self, x, A, interpolation=None, fill_seg=False):
        """
        :param x: 4D image tensor (batch_size x height x width x channels)
        :param A: 3D stack of affine (batch_size x 3 x 3) type is always float32
        """

        tr = tfa.image.transform_ops.matrices_to_flat_transforms(A)
        x = tfa.image.transform(x, tr, interpolation or self.interpolation)

        if fill_seg:
            mask = tfa.image.transform(tf.zeros_like(x[..., :1]), tr, interpolation or self.interpolation,
                                       fill_value=1.0)
            x += mask * self.fill_seg_value

        return x

    def __call__(self, shape, seed):
        sh = shape
        origin = tf.cast(sh[1:3], np.float32)[None] / 2 * tf.ones((sh[0], 1))

        flip = (self.flip_up_down, self.flip_left_right)

        mask_rotate = tf.cast(tf.random.uniform(sh[:1], seed=seed) < self.rotate_chance, tf.float32)

        rotate = self.rotate
        try:
            iter(rotate)
        except TypeError:
            rotate = [-rotate, rotate]
        rotate = np.array(rotate) * np.pi / 180
        rotate = tf.random.uniform(sh[:1], *rotate, seed=seed + 1) * mask_rotate

        mask_flip = tf.cast(tf.random.uniform(sh[:1], seed=seed) < self.chance, tf.float32)
        if flip[0]:
            flip1 = tf.sign(tf.random.uniform(sh[:1], -1, 1, seed=seed + 2)) * mask_flip + (1-mask_flip)
        else:
            flip1 = tf.ones_like(origin[:, 0])
        if flip[1]:
            flip2 = tf.sign(tf.random.uniform(sh[:1], -1, 1, seed=seed + 3)) * mask_flip + (1-mask_flip)
        else:
            flip2 = tf.ones_like(origin[:, 0])

        mask_scale_shear = tf.cast(tf.random.uniform(sh[:1], seed=seed + 4) < self.chance, tf.float32)
        scale = self.scale
        try:
            iter(scale)
        except TypeError:
            scale = [-scale, scale]
        scale = tf.random.uniform(sh[:1], *scale, seed=seed + 5) * mask_scale_shear
        shear = self.shear
        try:
            iter(shear)
        except TypeError:
            shear = [-shear, shear]
        shear1 = tf.random.uniform(sh[:1], *shear, seed=seed + 8) * mask_scale_shear
        shear2 = tf.random.uniform(sh[:1], *shear, seed=seed + 9) * mask_scale_shear

        mask_translate = tf.cast(tf.random.uniform(sh[:1], seed=seed) < self.chance, tf.float32)
        translate = [[-self.translate_vertical, self.translate_vertical],
                     [-self.translate_horizontal, self.translate_horizontal]]

        translate = tf.convert_to_tensor(translate) * tf.cast(sh[1:3], tf.float32)[:, None]
        translate1 = tf.random.uniform(sh[:1], translate[0, 0], translate[0, 1], seed=seed + 6) * mask_translate
        translate2 = tf.random.uniform(sh[:1], translate[1, 0], translate[1, 1], seed=seed + 7) * mask_translate

        A = affine(origin[:, 0], origin[:, 1], flip1, flip2, scale, rotate, shear1, shear2, translate1, translate2)
        return A


class ImageDeformation(vue.VueSettingsModule):
    def __init__(self, alpha: float = 0.0, sigma: float = 0.5, chance: float = 0.5):
        self.alpha = alpha
        self.sigma = sigma
        self.chance = chance

    def __call__(self, shape, seed):
        deformations = tf.random.uniform((shape[0], shape[1], shape[2], 2), seed=seed+114)
        probabilities = tf.random.uniform((shape[0], ), seed=seed + 113)
        return deformations, probabilities

    def deform_image(self, inputs, interpolation="bilinear"):
        x, dxy, do_deform = inputs
        if do_deform < self.chance:
            shape = tf.shape(x)
            dxy = gaussian_blur(dxy[None] * 2 - 1, self.sigma) * self.alpha
            if interpolation and interpolation == "nearest":
                dxy = tf.round(dxy)

            gx, gy = tf.meshgrid(tf.range(shape[1], dtype=tf.float32), tf.range(shape[0], dtype=tf.float32), indexing="xy")
            grid = tf.stack([gx + dxy[..., 0],
                             gy + dxy[..., 1]], -1)
            return tfa.image.resampler(x[None], grid)[0]
        else:
            return x

    def apply(self, x, deformations, probabilities, interpolation="bilinear"):
        """Elastic deformation of images as described in [Simard2003]_ (with modifications).
        .. [Simard2003] Simard, Steinkraus and Platt, "Best Practices for
             Convolutional Neural Networks applied to Visual Document Analysis", in
             Proc. of the International Conference on Document Analysis and
             Recognition, 2003.

         Based on https://gist.github.com/erniejunior/601cdf56d2b424757de5
        """

        deformation = tf.map_fn(fn=partial(self.deform_image, interpolation=interpolation),
                                elems=(x, deformations,probabilities), dtype=x.dtype)
        return deformation


class ImageSaltAndPepper(vue.VueSettingsModule):
    def __init__(self, fraction: float = 0.0002, value_range: tuple = None, scale: int = 1, chance: float = 0.5):
        """
        :param brightness: Embossing in a random direction with a scale chosen in the given range
        :param contrast: Size of mean filtering kernel
        :param hue:
        :param saturation:
        :param stddev:
        :param chance: The chance of the individual step to be applied
        """
        self.fraction = fraction
        self.value_range = value_range or (0.0, 1.0)
        self.scale = scale
        assert scale in [1, 3, 5]
        self.chance = chance

        self.fractions = (self.fraction / 2, 1.0-self.fraction / 2)

    def apply_noise(self, inputs):
        x, salt_pepper, prob_salt_pepper = inputs
        if prob_salt_pepper < self.chance:
            if self.scale == 5:
                sp = tf.cast(-tf.nn.max_pool2d(-salt_pepper[None], (1, 5, 5, 1), (1, 1, 1, 1), "SAME") < self.fractions[0], tf.float32)[0] * \
                     self.value_range[0] + \
                     tf.cast(tf.nn.max_pool2d(salt_pepper[None], (1, 5, 5, 1), (1, 1 ,1, 1), "SAME") > self.fractions[1], tf.float32)[0] * \
                     self.value_range[1]
            elif self.scale == 3:
                sp = tf.cast(-tf.nn.max_pool2d(-salt_pepper[None], (1, 3, 3, 1), (1, 1, 1, 1), "SAME") < self.fractions[0], tf.float32)[0] * \
                     self.value_range[0] + \
                     tf.cast(tf.nn.max_pool2d(salt_pepper[None], (1, 3, 3, 1), (1, 1 ,1, 1), "SAME") > self.fractions[1], tf.float32)[0] * \
                     self.value_range[1]
            elif self.scale == 1:
                sp = tf.cast(salt_pepper < self.fractions[0], tf.float32) * self.value_range[0] + \
                     tf.cast(salt_pepper > self.fractions[1], tf.float32) * self.value_range[1]
            return sp
        else:
            return tf.zeros_like(salt_pepper)

    def __call__(self, x, seed):
        sh = tf.shape(x)

        salt_pepper = tf.random.uniform(shape=sh[:3], minval=0.0, maxval=1.0, dtype=tf.float32, seed=seed+111)[..., None]

        prob_salt_pepper = tf.random.uniform((sh[0], ), seed=seed+112)
        return tf.map_fn(self.apply_noise, [x, salt_pepper, prob_salt_pepper], dtype=tf.float32)


class ImageNoise(vue.VueSettingsModule):
    def __init__(self, brightness: float = 0.25, contrast: tuple = (0.5, 1.25),
                 hue: float = 0.05, saturation: tuple = (0, 2.0), stddev: float = 0.01, chance: float = 0.5):
        """
        :param brightness: Embossing in a random direction with a scale chosen in the given range
        :param contrast: Size of mean filtering kernel
        :param hue:
        :param saturation:
        :param stddev:
        :param chance: The chance of the individual step to be applied
        """
        self.brightness = brightness
        self.contrast = contrast or (0.5, 1.25)
        self.hue = hue
        self.saturation = saturation or (0, 2.0)
        self.stddev = stddev
        self.chance = chance

    def conditional_noise(self, inputs):
        x, hue, saturation, prob_hue_sat, contrast, prob_contrast, brightness, prob_brightness, noise, prob_noise = inputs
        sh = tf.shape(x)

        if sh[2] == 3 and prob_hue_sat < self.chance:
            x = tf.image.adjust_saturation(x, saturation)
            x = tf.image.adjust_hue(x, hue)

        if prob_contrast < self.chance:
            x = tf.image.adjust_contrast(x, contrast)

        if prob_brightness < self.chance:
            x = tf.image.adjust_brightness(x, brightness)

        if prob_noise < self.chance:
            x = tf.add(x, noise)
        return x

    def __call__(self, x, seed):
        sh = tf.shape(x)

        hue = tf.random.uniform((sh[0], ), -self.hue, self.hue, seed=seed + 100)
        saturation = tf.random.uniform((sh[0], ), self.saturation[0], self.saturation[1], seed=seed+101)
        prob_hue_sat = tf.random.uniform((sh[0],), seed=seed+102)

        contrast = tf.random.uniform((sh[0], ), self.contrast[0], self.contrast[1], seed=seed+103)
        prob_contrast = tf.random.uniform((sh[0],), seed=seed+104)

        brightness = tf.random.uniform((sh[0], ), -self.brightness, self.brightness, seed=seed+105)
        prob_brightness = tf.random.uniform((sh[0],), seed=seed+106)

        noise = tf.random.normal(shape=tf.shape(x), mean=0, stddev=self.stddev,
                                 dtype=tf.float32, seed=seed+107)
        prob_noise = tf.random.uniform((sh[0],), seed=seed+108)

        return tf.map_fn(self.conditional_noise, [x,
                                                  hue, saturation, prob_hue_sat,
                                                  contrast, prob_contrast,
                                                  brightness, prob_brightness,
                                                  noise, prob_noise], dtype=tf.float32)


class ImageFiltering(vue.VueSettingsModule):
    def __init__(self, emboss_strength: tuple = None, avg_blur: tuple = (3, 3), gaussian_blur_sigma: float = 0.5,
                 chance: float = 0.5):
        """
        :param emboss_strength: Embossing in a random direction with a scale chosen in the given range
        :param avg_blur: Size of mean filtering kernel
        :param gaussian_blur_sigma:
        :param chance: The chance of the individual step to be applied
        """
        self.emboss_strength = emboss_strength or (0, 0.25)
        self.avg_blur = avg_blur or (3, 3)
        self.gaussian_blur_sigma = gaussian_blur_sigma
        self.chance = chance

    def conditional_filter(self, inputs):
        x, probability, emboss_xy = inputs
        if probability < self.chance / 3:
            # Emboss
            dxy = tf.image.sobel_edges(x[None])[0]
            emboss = tf.reduce_sum(emboss_xy * dxy, axis=-1)
            return x + emboss
        elif probability < 2 * self.chance / 3:
            # Gaussian blur
            return gaussian_blur(x[None], self.gaussian_blur_sigma)[0]
        elif probability < 3 * self.chance / 3:
            # Average blur
            avg_blur_kernel =  tf.tile(_avg_kernel(self.avg_blur, x.dtype)[..., None, None], (1, 1, tf.shape(x)[-1], 1))
            return tf.nn.depthwise_conv2d(x[None], avg_blur_kernel, [1, 1, 1, 1], 'SAME')[0]
        else:
            # No filtering
            return x

    def __call__(self, x, seed):
        sh = tf.shape(x)
        probabilities = tf.random.uniform((sh[0],), seed=seed+102)

        emboss_sign = tf.sign(tf.random.uniform((sh[0], 1, 1, sh[3], 2), -1, 1, seed=seed + 103))
        emboss_xy = emboss_sign * tf.random.uniform((sh[0], 1, 1, sh[3], 2), self.emboss_strength[0],
                                                    self.emboss_strength[1], seed=seed + 104)
        return tf.map_fn(self.conditional_filter, [x, probabilities, emboss_xy], dtype=tf.float32)


class ViewGlimpseFromBBox(vue.VueSettingsModule):
    def __init__(self, bbox_key=None,
                 target_shape: tuple = None, zoom_factor: int = None):
        self.bbox_key = bbox_key or ImageKeys.BOUNDING_BOX
        self.target_shape = target_shape

        # Ensure zoom_factor is not 0
        self.zoom_factor = None if zoom_factor == 0 else zoom_factor

        if self.zoom_factor:
            assert np.log2(self.zoom_factor).is_integer(), \
                f"zoom_exp_factor '{self.zoom_factor}' must be a power of 2"

    @property
    def bbox_shape(self):
        if self.zoom_factor: # not zero or None
            return tuple(int(x * self.zoom_factor) for x in self.target_shape)
        else:
            return self.target_shape

    def __call__(self, x, seed):
        # Extract info
        img_size = tf.cast(x[ImageKeys.SIZE], tf.int32)
        views = tf.cast(x[self.bbox_key], tf.int32)

        # Choose glimpse in bbox
        offset_scales = views[:, 2:] - views[:, :2] + self.bbox_shape
        offsets = tf.random.uniform(tf.shape(offset_scales), seed=seed + 201) * tf.cast(offset_scales, tf.float32)
        view_center = views[:, :2] + tf.cast(tf.round(offsets), tf.int32)
        view_origin = view_center - self.bbox_shape

        # Clip bbox to boundaries of image
        max_idx = img_size - self.bbox_shape
        min_idx = tf.zeros_like(max_idx, dtype=tf.int32)
        view_origin = tf.clip_by_value(view_origin, min_idx, max_idx)

        # Update bbox
        views = tf.concat([view_origin, view_origin + tf.constant(self.bbox_shape)[None]], axis=1)
        x[self.bbox_key] = views

        # Add zoom to dataset
        if self.zoom_factor is not None:
            # Create tensor of shape (batch_size,) with value self.zoom_factor
            zef = tf.constant(self.zoom_factor, dtype=tf.float32, shape=(1,))
            x[ImageKeys.ZOOM] = tf.broadcast_to(zef, tf.shape(x[self.bbox_key])[:1])
        return x


class ViewGlimpseFromPoints(vue.VueSettingsModule):
    def __init__(self, bbox_key=None, target_shape: tuple = None, zoom_factor: int = None, overlap: int = 0.8):
        self.bbox_key = bbox_key or ImageKeys.BOUNDING_BOX
        self.target_shape = target_shape

        # Ensure zoom_factor is not 0
        self.zoom_factor = None if zoom_factor == 0 else zoom_factor

        self.overlap = overlap

        if self.zoom_factor and not np.log2(self.zoom_factor).is_integer():
            log.warning(f"zoom_exp_factor '{self.zoom_factor}' must be a power of 2 for tiled images to work")

    @property
    def bbox_shape(self):
        if self.zoom_factor: # not zero or None
            return tuple(int(x * self.zoom_factor) for x in self.target_shape)
        else:
            return self.target_shape

    def __call__(self, x, seed):
        inside_points = x[ImageKeys.INSIDE_POINTS]
        sh = tf.shape(inside_points)

        if ImageKeys.BBOX_SIZE_ADJUST in x:
            bbox_adjust = tf.cast(x[ImageKeys.BBOX_SIZE_ADJUST], tf.float32)
            adjusted_bbox_shape = bbox_adjust[:, None] * self.bbox_shape
            x[ImageKeys.ZOOM] = tf.round(adjusted_bbox_shape)[:, 0] / self.bbox_shape[0]
        else:
            adjusted_bbox_shape = tf.constant(self.bbox_shape, dtype=tf.float32)[None]

        # Choose target point
        choice = tf.random.uniform(shape=(sh[0],), maxval=sh[1], dtype=tf.int32, seed=seed + 202)
        target_points = tf.gather_nd(inside_points, indices=tf.stack([tf.range(sh[0]), choice], axis=-1))

        # Adjust bbox
        half_size = tf.cast(tf.round(adjusted_bbox_shape / 2), tf.int32)
        overlap_px = tf.cast(half_size, tf.float32) * self.overlap
        offset = tf.random.uniform(tf.shape(target_points), minval=-1, maxval=1, seed=seed + 201) * overlap_px
        view_origin = target_points - half_size + tf.cast(offset, tf.int32)

        # Clip bbox to boundaries of image
        img_size = tf.cast(x[ImageKeys.SIZE], tf.int32)
        max_idx = img_size - self.bbox_shape
        min_idx = tf.zeros_like(max_idx, dtype=tf.int32)
        view_origin = tf.clip_by_value(view_origin, min_idx, max_idx)

        # Update bbox
        views = tf.concat([view_origin, view_origin + tf.cast(tf.round(adjusted_bbox_shape), tf.int32)], axis=1)
        x[self.bbox_key] = views

        # Add zoom to dataset
        if self.zoom_factor is not None:
            # Create tensor of shape (batch_size,) with value self.zoom_factor
            zef = tf.constant(self.zoom_factor, dtype=tf.float32, shape=(1,))
            zef = tf.broadcast_to(zef, tf.shape(x[self.bbox_key])[:1])
            x[ImageKeys.ZOOM] = zef * x[ImageKeys.ZOOM] if ImageKeys.ZOOM in x else zef

        return x


class ImageAugmenter(vue.VueSettingsModule):
    def __init__(self, image_keys=None, label_keys=None,
                 random_transformer: RandomTransformer = RandomTransformer(),
                 image_noise: ImageNoise = ImageNoise(),
                 image_filter: ImageFiltering = ImageFiltering(),
                 image_deformation: ImageDeformation = None):
        """
        Image augmentation class, for use with tensorflow and criterion datasets
        The call method expects a tensor dict with image and label keys for transformation.
        Alternatively, the augmenter may be used by calling transform_images directly

        :param image_keys: labels of images to perform augmentation on
        :param label_keys: labels of annotations to perform augmentation on
        :param random_transformer: A random affine transformation object with RandomTransformer interfaces
        :param image_noise: An image noise generation object with ImageNoise interfaces
        :param image_filter: An image filter noise generation object with ImageFiltering interfaces
        :param image_deformation: A local random image deformation object with ImageDeformation interfaces

        """
        self.image_keys = image_keys or ["img"]
        self.label_keys = label_keys or ["segmentation"]
        self.random_transformer = random_transformer
        self.image_noise = image_noise
        self.image_filter = image_filter
        self.image_deformation = image_deformation
        pass

    def __call__(self, x, seed, *args, **kwargs):
        A = deformations = probabilities = None

        if self.random_transformer is not None:
            A = self.random_transformer(tf.shape(x[self.image_keys[0]]), seed=seed)
        if self.image_deformation is not None:
            deformations, probabilities = self.image_deformation(tf.shape(x[self.image_keys[0]]), seed)

        for key in self.image_keys:
            if key in x:
                if self.random_transformer is not None:
                    x[key] = self.random_transformer.transform_images(x[key], A)
                if self.image_deformation is not None:
                    x[key] = self.image_deformation.apply(x[key], deformations, probabilities)
                if self.image_filter is not None:
                    x[key] = self.image_filter(x[key], seed=seed)
                if self.image_noise is not None:
                    x[key] = self.image_noise(x[key], seed=seed)

        for key in self.label_keys:
            if key in x:
                if self.random_transformer is not None:
                    x[key] = self.random_transformer.transform_images(tf.cast(x[key], tf.float32), A,
                                                                      interpolation="nearest", fill_seg=True)
                if self.image_deformation is not None:
                    x[key] = self.image_deformation.apply(tf.cast(x[key], tf.float32), deformations, probabilities, interpolation="nearest")
        return x

    @classmethod
    def to_schema(cls, builder, name, ptype, default, **kwargs):

        if name in {"image_keys", "label_keys"}:
            return
        else:
            return super().to_schema(builder=builder, name=name, ptype=ptype, default=default, **kwargs)



# DEPRECATED
def get_transform_schema(ns):
    return [
        vue.number_input("Vertical translation range in percent", ns + "translate_vertical", default=0.1, required=False, visible=False),
        vue.number_input("Horizontal translation range in percent", ns + "translate_horizontal", default=0.1, required=False, visible=False),
        vue.number_input("Maximum scale offset", ns + "scale", default=0.2, required=False, visible=False),
        vue.number_input("Maximum relative shear", ns + "shear", default=0.04, required=False, visible=False),
        vue.number_input("Maximum rotation angle", ns + "rotate", default=90, required=False, visible=False),
        vue.checkbox("Flip up-down", ns + "flip_up_down", default=True, required=False, visible=False),
        vue.checkbox("Flip left-right", ns + "flip_left_right", default=True, required=False, visible=False),
        vue.number_input("Chance of augmentation steps", ns + "chance", default=0.5, required=False, visible=False)
    ]


# DEPRECATED
def get_noise_schema(ns):
    return [
        vue.number_input("Maximum brightness delta", ns + "brightness", default=0.25, required=False, visible=False),
        vue.text_input("Emboss alpha range", ns + "emboss_alpha",
                       required=False, default="[0.0, 0.1]", json=True),
        vue.text_input("Emboss strength range", ns + "emboss_alpha",
                       required=False, default="[0.75, 1.25]", json=True),
        vue.text_input("Image saturation range", ns + "saturation",
                       required=False, default="[0, 2.0]", json=True),
        vue.number_input("Maximum hue delta", ns + "hue", default=0.05, required=False, visible=False),
        vue.number_input("Maximum white noise", ns + "stddev", default=0.01, required=False, visible=False),
        vue.number_input("Chance of augmentation steps", ns + "chance", default=0.5, required=False, visible=False)
    ]

# DEPRECATED
class ImageAugmentationSchema(vue.SchemaBuilderFunc):
    label = "Image Augmentation"
    ns = "augmentation"
    advanced = False
    module = ImageAugmenter

    def schema(self, b=vue.SchemaBuilder(), ns=ns, **kwargs):
        b += get_transform_schema(ns=ns+"transform.")
        b += get_noise_schema(ns=ns+"noise.")
        return b